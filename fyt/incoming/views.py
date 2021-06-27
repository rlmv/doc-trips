import io
import logging

import django_tables2 as tables
from braces.views import FormMessagesMixin
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from vanilla import CreateView, FormView, TemplateView, UpdateView

from .filters import RegistrationFilterSet
from .forms import AssignmentForm, PyExcelFileForm, RegistrationForm, TrippeeInfoForm
from .models import IncomingStudent, Registration, Settings
from .tables import IncomingStudentTable, RegistrationTable

from fyt.core.models import TripsYear
from fyt.core.views import (
    DatabaseCreateView,
    DatabaseDeleteView,
    DatabaseDetailView,
    DatabaseListView,
    DatabaseUpdateView,
    TripsYearMixin,
)
from fyt.permissions.views import DatabaseEditPermissionRequired
from fyt.timetable.models import Timetable
from fyt.trips.models import TripType
from fyt.users.models import DartmouthUser
from fyt.utils.forms import crispify
from fyt.utils.views import ExtraContextMixin


"""
Views for incoming students.

The first set of views are public facing and allow incoming
students to register for trips. The second set handle manipulation of
registrations and trippees in the database.

"""

logger = logging.getLogger(__name__)


class IfRegistrationAvailable:
    """
    Redirect if trippee registration is not currently available
    """

    def dispatch(self, request, *args, **kwargs):

        if not Timetable.objects.timetable().registration_available():
            return HttpResponseRedirect(reverse('incoming:registration_not_available'))
        return super().dispatch(request, *args, **kwargs)


class RegistrationNotAvailable(TemplateView):
    """
    View shown if registration is not available.
    """

    template_name = 'incoming/not_available.html'


class BaseRegistrationView(
    LoginRequiredMixin, IfRegistrationAvailable, FormMessagesMixin, TripsYearMixin
):
    """
    CBV base for registration form with all contextual information
    """

    model = Registration
    form_class = RegistrationForm
    template_name = 'incoming/register.html'
    success_url = reverse_lazy('incoming:portal')
    form_valid_message = "Your registration has been saved"
    form_invalid_message = (
        "Uh oh, it looks like there's an error somewhere in your "
        "registration. Please fix the error and submit the form again."
    )

    @cached_property
    def trips_year(self):
        return TripsYear.objects.current()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['triptypes'] = TripType.objects.visible(self.trips_year)
        context[
            'registration_deadline'
        ] = Timetable.objects.timetable().trippee_registrations_close
        context['contact_url'] = Settings.objects.get(
            trips_year=self.trips_year
        ).contact_url
        return context


class Register(BaseRegistrationView, CreateView):
    """
    Register for trips

    Redirect to the edit view if this incoming student
    has already registered.
    """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Redirect to edit existing application

        This is redundantly decorated with login_required to prevent user
        from being anonymous. Otherwise this gets called first in the MRO
        order *then* passed to the LoginRequiredMixin, which doesn't work.
        """
        reg = Registration.objects.filter(
            trips_year=self.trips_year, user=request.user
        ).first()
        if reg:
            return HttpResponseRedirect(reverse('incoming:edit_registration'))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form, **kwargs):
        """
        Add the registering user to the registration

        The registration will be automagically matched with a
        corresponding IncomingStudent model if it exists.
        """
        self.object = form.save(self.request.user)
        self.object.match()

        return HttpResponseRedirect(self.get_success_url())


class EditRegistration(BaseRegistrationView, UpdateView):
    """
    Edit a trips registration.
    """

    def get_object(self):
        """
        Get registration for user
        """
        return get_object_or_404(
            self.model, user=self.request.user, trips_year=self.trips_year
        )


class IncomingStudentPortal(LoginRequiredMixin, ExtraContextMixin, TemplateView):
    """
    Information for incoming students.

    Shows trip assignment, if available, and link to registration.
    """

    template_name = 'incoming/portal.html'

    @cached_property
    def trips_year(self):
        return TripsYear.objects.current()

    def get_registration(self):
        """
        Return current user's registration, or None if DNE.
        """
        try:
            return Registration.objects.get(
                user=self.request.user, trips_year=self.trips_year
            )
        except Registration.DoesNotExist:
            return None

    def get_incoming_student(self):
        """
        Return user's incoming student data, or None if DNE.
        """
        try:
            return IncomingStudent.objects.get(
                netid=self.request.user.netid, trips_year=self.trips_year
            )
        except IncomingStudent.DoesNotExist:
            return None
        except MultipleObjectsReturned as exc:
            logger.error(exc, extra={'request': self.request, 'stack': True})
            raise exc

    def extra_context(self):
        timetable = Timetable.objects.timetable()
        reg = self.get_registration()
        inc = self.get_incoming_student()

        return {
            'registration': reg,
            'incoming_student': inc,
            'trip': inc.trip_assignment if inc else None,
            'registration_available': timetable.registration_available(),
            'registration_closes': timetable.trippee_registrations_close,
            'after_deadline': (timetable.trippee_registrations_close > timezone.now()),
            'assignment_available': timetable.trippee_assignment_available,
            'trips_year': self.trips_year,
            'contact_url': (
                Settings.objects.get(trips_year=self.trips_year).contact_url
            ),
        }


# ----- database internal views --------


class RegistrationIndex(DatabaseListView):
    """
    All trippee registrations.
    """

    model = Registration
    template_name = 'incoming/registration_index.html'
    context_object_name = 'registrations'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            'trippee',
            'trippee__trip_assignment__section',
            'trippee__trip_assignment__template',
        )

    def extra_context(self):
        filter = RegistrationFilterSet(
            self.request.GET, queryset=self.get_queryset(), trips_year=self.trips_year
        )
        return {
            'table': RegistrationTable(filter.qs, self.request),
            'filter': filter,
            'registration_count': len(filter.qs),
            'unmatched': Registration.objects.unmatched(self.trips_year),
        }


class NonStudentRegistration(DatabaseCreateView):
    """
    Used to register a non-student for trips.

    This was needed because a TA was going on trips but
    would not be assigned a netid until mid-September.
    We needed some way to put her in the system. She won't
    be able to log in and see her assignment, but she can be
    assigned to a trip.

    This view creates a user object without a netid and links the registration
    to this user.
    """

    model = Registration
    form_class = RegistrationForm
    explanation = (
        "<p> Upload a registration for a non-student. Use this only "
        "if, for some reason, the trippee does not have a NetId. "
        "An Incoming Student object will be automatically created "
        "and filled in with information from the registration. </p>"
    )

    def form_valid(self, form):
        with transaction.atomic():
            user = DartmouthUser.objects.create_user_without_netid(
                form.cleaned_data['name'], form.cleaned_data['email']
            )
            self.object = form.save(user=user)

            IncomingStudent.objects.create(
                trips_year=self.trips_year,
                name=self.object.name,
                netid=user.netid,
                email=self.object.email,
                blitz=self.object.email,
                phone=self.object.phone,
                gender=self.object.gender,
                registration=self.object,
            )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.object.trippee.detail_url()


class RegistrationDetail(DatabaseDetailView):
    model = Registration

    fields = [
        ('Incoming Student data', 'get_incoming_student'),
        ('Submitted at', 'created_at'),
        'updated_at',
        'name',
        ('NetId', 'netid'),
        'gender',
        'previous_school',
        'phone',
        'email',
        'guardian_email',
        'is_exchange',
        'is_transfer',
        'is_international',
        'is_native',
        'is_fysep',
        'is_athlete',
        ('first choice trip types', 'new_firstchoice_triptypes'),
        ('preferred trip types', 'new_preferred_triptypes'),
        ('available trip types', 'new_available_triptypes'),
        'tshirt_size',
        'height',
        'weight',
        'food_allergies',
        'dietary_restrictions',
        'medical_conditions',
        'epipen',
        'needs',
        'regular_exercise',
        'physical_activities',
        'other_activities',
        'swimming_ability',
        'camping_experience',
        'hiking_experience',
        ('please describe your hiking experience', 'hiking_experience_description'),
        'has_boating_experience',
        'boating_experience',
        'other_boating_experience',
        'fishing_experience',
        'horseback_riding_experience',
        'mountain_biking_experience',
        'sailing_experience',
        'anything_else',
        'financial_assistance',
        'waiver',
        'doc_membership',
        'green_fund_donation',
        'final_request',
    ]


class RegistrationUpdate(DatabaseUpdateView):
    """
    Edit a registration.
    """

    model = Registration
    form_class = RegistrationForm


class RegistrationDelete(DatabaseDeleteView):
    """
    Delete a registration.
    """

    model = Registration
    success_url_pattern = 'core:registration:index'


class IncomingStudentIndex(tables.views.SingleTableMixin, DatabaseListView):
    """
    All incoming students
    """

    model = IncomingStudent
    table_class = IncomingStudentTable
    table_pagination = False
    template_name = 'incoming/trippee_index.html'
    context_object_name = 'trippees'

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                'trip_assignment__section',
                'trip_assignment__template',
                'bus_assignment_round_trip',
                'bus_assignment_to_hanover',
                'bus_assignment_from_hanover',
            )
        )


class IncomingStudentDetail(DatabaseDetailView):
    model = IncomingStudent
    template_name = 'incoming/trippee_detail.html'
    context_object_name = 'trippee'

    admin_fields = (
        'registration',
        'financial_aid',
        'cancelled',
        'cancelled_fee',
        ('total cost', 'compute_cost'),
        'hide_med_info',
        'med_info',
        'decline_reason',
        'notes',
    )
    college_fields = (
        'name',
        'netid',
        'class_year',
        'gender',
        'birthday',
        'ethnic_code',
        'incoming_status',
        'email',
        'blitz',
        'phone',
        'address',
        'hinman_box',
    )

    def extra_context(self):
        return {
            'edit_assignment_url': reverse(
                'core:incomingstudent:update_assignment', kwargs=self.kwargs
            ),
            'edit_admin_url': reverse(
                'core:incomingstudent:update', kwargs=self.kwargs
            ),
        }


class IncomingStudentDelete(DatabaseDeleteView):
    """
    Delete an incoming student.
    """

    model = IncomingStudent
    success_url_pattern = 'core:incomingstudent:index'


class UpdateTripAssignment(DatabaseUpdateView):
    """
    Edit trip and bus assignments for an incoming student.
    """

    model = IncomingStudent
    template_name = 'incoming/update_trip.html'
    form_class = AssignmentForm

    def extra_context(self):
        reg = self.object.get_registration()
        context = {'registration': reg}
        if reg:
            context['firstchoice_trips'] = reg.get_firstchoice_trips()
            context['preferred_trips'] = reg.get_preferred_trips()
            context['available_trips'] = reg.get_available_trips()

        return context


class IncomingStudentUpdate(DatabaseUpdateView):
    """
    Edit other incoming student information.
    """

    model = IncomingStudent
    context_object_name = 'trippee'
    form_class = TrippeeInfoForm
    delete_button = False


class UploadIncomingStudentData(
    DatabaseEditPermissionRequired, TripsYearMixin, FormView
):
    """
    Accept an upload of CSV file of incoming students.

    Parses the CSV file and adds the data to the database as
    IncomingStudent objects.

    .. todo:: parse or input the status of the incoming student
    .. todo:: simplify and document the column names
    """

    form_class = PyExcelFileForm
    template_name = 'incoming/upload_incoming_students.html'

    def form_valid(self, form):
        try:
            (ctd, skipped) = IncomingStudent.objects.create_from_sheet(
                form.load_sheet(), self.trips_year
            )

            if ctd:
                msg = 'Created incoming students with NetIds %s'
                logger.info(msg % ctd)
                messages.info(self.request, msg % ctd)

            if skipped:
                msg = 'Ignored existing incoming students with NetIds %s'
                logger.info(msg % skipped)
                messages.warning(self.request, msg % skipped)

        except KeyError as exc:
            msg = "A column is missing (or mis-named) in the uploaded file: %s"
            messages.error(self.request, msg % exc)

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path


class UploadHinmanBoxes(DatabaseEditPermissionRequired, TripsYearMixin, FormView):
    """
    Upload a CSV file of netids and hinman box numbers.
    Update the cooresponding IncomingStudent's HB #s.
    """

    form_class = PyExcelFileForm
    template_name = 'incoming/upload_hinman_boxes.html'

    def form_valid(self, form):
        updated, not_found = IncomingStudent.objects.update_hinman_boxes(
            form.load_sheet(), self.trips_year
        )

        msg = "Not found: %s" % ", ".join(not_found)
        messages.error(self.request, msg)

        msg = "Updated Hinman Boxes for: %s" % ", ".join(map(str, updated))
        messages.info(self.request, msg)
        return HttpResponseRedirect(self.request.path)


class MatchRegistrations(DatabaseEditPermissionRequired, TripsYearMixin, FormView):
    """
    Match all registrations for this ``trips_year``.

    Backdoor solution in case auto-matching is not
    working.

    .. todo:: expose this with a link
    """

    template_name = 'db/form.html'

    def get_form(self, **kwargs):
        return crispify(forms.Form(**kwargs), 'Match')

    def form_valid(self, form):
        """
        Try and match all unmatched registrations.
        """
        regs = Registration.objects.filter(trips_year=self.trips_year)
        matches = []
        for reg in regs:
            if not hasattr(reg, 'trippee'):
                matches.append(reg.match())
        messages.info(self.request, 'Matched %s' % list(filter(None, matches)))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('core:registration:match', kwargs=self.kwargs)


class EditSettings(DatabaseUpdateView):
    """
    Edit Registration settings - cost, contact info
    """

    model = Settings
    template_name = 'form.html'
    delete_button = False

    def get_headline(self):
        return "Registration Settings"

    @property
    def trips_year(self):
        return self.current_trips_year

    def get_object(self):
        return Settings.objects.get(trips_year=self.trips_year)

    def get_success_url(self):
        return self.request.path
