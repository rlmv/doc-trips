import io
import logging

from django import forms
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.decorators import method_decorator
from vanilla import CreateView, UpdateView, DetailView, TemplateView, ListView, FormView
from braces.views import LoginRequiredMixin, FormMessagesMixin
from django_tables2 import RequestConfig

from .models import Registration, IncomingStudent
from .tables import RegistrationTable
from .forms import (RegistrationForm, UploadIncomingStudentsForm,
                    AssignmentForm, TrippeeInfoForm)
from doc.core.models import Settings
from doc.db.models import TripsYear
from doc.db.views import (
    TripsYearMixin, DatabaseUpdateView, DatabaseDeleteView, DatabaseListView,
    DatabaseCreateView, DatabaseDetailView
)
from doc.permissions.views import (DatabaseReadPermissionRequired,
                                   DatabaseEditPermissionRequired)
from doc.timetable.models import Timetable
from doc.trips.models import TripType
from doc.users.models import DartmouthUser
from doc.utils.forms import crispify

"""
Views for incoming students.

The first set of views are public facing and allow incoming 
students to register for trips. The second set handle manipulation of
registrations and trippees in the database.

"""

logger = logging.getLogger(__name__)


class IfRegistrationAvailable():
    """ 
    Redirect if trippee registration is not currently available 
    """
    def dispatch(self, request, *args, **kwargs):
        
        if not Timetable.objects.timetable().registration_available():
            return HttpResponseRedirect(
                reverse('incoming:registration_not_available')
            )
        return super(IfRegistrationAvailable, self).dispatch(request, *args, **kwargs)


class RegistrationNotAvailable(TemplateView):
    """
    View shown if registration is not available.
    """
    template_name = 'incoming/not_available.html'


class BaseRegistrationView(LoginRequiredMixin, IfRegistrationAvailable,
                           FormMessagesMixin):
    """
    CBV base for registration form with all contextual information 
    """
    model = Registration
    template_name = 'incoming/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('incoming:portal')
    form_valid_message = "Your registration has been saved"
    form_invalid_message = (
        "Uh oh, it looks like there's an error somewhere in your "
        "registration. Please fix the error and submit the form again."
    )

    def get_context_data(self, **kwargs):
        context = super(BaseRegistrationView, self).get_context_data(**kwargs)
        context['triptypes'] = TripType.objects.filter(
            trips_year=TripsYear.objects.current())
        context['registration_deadline'] = (
            Timetable.objects.timetable().trippee_registrations_close)
        context['trips_year'] = TripsYear.objects.current()
        context['contact_url'] = Settings.objects.get().contact_url
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
            trips_year=TripsYear.objects.current(),
            user=request.user).first()
        if reg:
            return HttpResponseRedirect(reverse('incoming:edit_registration'))

        return super(Register, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form, **kwargs):
        """ 
        Add the registering user to the registration 

        The registration will be automagically matched with a 
        corresponding IncomingStudent model if it exists.
        """
        form.instance.trips_year = TripsYear.objects.current()
        form.instance.user = self.request.user

        self.object = form.save()
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
            self.model, user=self.request.user,
            trips_year=TripsYear.objects.current()
        )


class IncomingStudentPortal(LoginRequiredMixin, TemplateView):
    """
    Information for incoming students.

    Shows trip assignment, if available, and link to registration.
    """
    template_name = 'incoming/portal.html'
    
    def get_registration(self):
        """
        Return current user's registration, or None if DNE.
        """
        try:
            return Registration.objects.get(
                user=self.request.user,
                trips_year=TripsYear.objects.current()
            )
        except Registration.DoesNotExist:
            return None

    def get_incoming_student(self):
        """
        Return user's incoming student data, or None if DNE.
        """
        try:
            return IncomingStudent.objects.get(
                netid=self.request.user.netid,
                trips_year=TripsYear.objects.current()
            )
        except IncomingStudent.DoesNotExist:
            return None
        except MultipleObjectsReturned as exc:
            logger.error(exc, extra={'request': self.request, 'stack': True})
            raise exc

    def get_context_data(self, **kwargs):
        timetable = Timetable.objects.timetable()
        kwargs['registration'] = reg = self.get_registration()
        kwargs['incoming_student'] = inc = self.get_incoming_student()
        kwargs['trip'] = inc.trip_assignment if inc else None
        kwargs['registration_available'] = timetable.registration_available()
        kwargs['registration_closes'] = timetable.trippee_registrations_close
        kwargs['after_deadline'] = (
            timetable.trippee_registrations_close > timezone.now())
        kwargs['assignment_available'] = timetable.trippee_assignment_available
        kwargs['contact_url'] = Settings.objects.get().contact_url
        kwargs['trips_year'] = TripsYear.objects.current()
        return super(IncomingStudentPortal, self).get_context_data(**kwargs)


# ----- database internal views --------


class RegistrationIndex(DatabaseListView):
    """ 
    All trippee registrations.
    """
    model = Registration
    template_name = 'incoming/registration_index.html'
    context_object_name = 'registrations'
    
    def get_queryset(self):
        qs = super(RegistrationIndex, self).get_queryset()
        return qs.select_related(
            'user',
            'trippee',
            'trippee__trip_assignment__section',
            'trippee__trip_assignment__template',
        )

    def get_context_data(self, **kwargs):
        kwargs['unmatched'] = (
            Registration.objects.unmatched(self.get_trips_year())
        )
        kwargs['table'] = RegistrationTable(self.object_list)
        RequestConfig(self.request, paginate=False).configure(kwargs['table'])
        return super(RegistrationIndex, self).get_context_data(**kwargs)


class NonStudentRegistration(DatabaseCreateView):
    """
    Used to register a non-student for trips.

    This was needed because a TA was going on trips but
    would not be assigned a netid until mid-September.
    We needed some way to put her in the system. She won't
    be able to log in and see her assignment, but she can be 
    assigned to a trip.

    This view creates a registration linked to the sentinel
    user, and an associated incoming student object.

    .. todo::
       I don't think this will handle more than one no-student
       registration per year because ``sentinel.netid`` is not unique.
    """
    model = Registration
    form_class = RegistrationForm
    explanation = (
        "<p> Upload a registration for a non-student. Use this only "
        "if, for some reason, the trippee does not have a NetId. "
        "An Incoming Student object will be automatically created "
        "and filled in with information from the registration. </p>")

    def form_valid(self, form):
        form.instance.trips_year_id = self.kwargs['trips_year']
        form.instance.user = DartmouthUser.objects.sentinel()
        self.object = form.save()
        IncomingStudent.objects.create(
            trips_year_id=self.kwargs['trips_year'],
            name=self.object.name,
            email=self.object.email,
            blitz=self.object.email,
            phone=self.object.phone,
            gender=self.object.gender,
            registration=self.object
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.object.trippee.detail_url()


class RegistrationDetail(DatabaseReadPermissionRequired,
                         TripsYearMixin, DetailView):
    model = Registration
    template_name = 'incoming/registration_detail.html'
    
    fields = [
        'name', 'gender', 'previous_school', 'phone', 'email',
        'guardian_email', 'is_exchange', 'is_transfer', 
        'is_international', 'is_native', 'is_fysep', 'is_athlete',
        'preferred_sections', 'available_sections', 'unavailable_sections',
        'firstchoice_triptype', 'preferred_triptypes',
        'available_triptypes', 'unavailable_triptypes',
        'schedule_conflicts', 'tshirt_size', 'medical_conditions',
        'allergies', 'allergen_information', 'epipen', 'needs',
        'dietary_restrictions', 'allergy_severity', 'allergy_reaction',
        'regular_exercise', 'physical_activities', 'other_activities',
        'swimming_ability', 'camping_experience',
        'hiking_experience',
        ('please describe your hiking experience', 'hiking_experience_description'),
        'has_boating_experience', 'boating_experience',
        'other_boating_experience', 'fishing_experience',
        'horseback_riding_experience', 'mountain_biking_experience',
        'sailing_experience', 'anything_else',
        'bus_stop_round_trip',
        'bus_stop_to_hanover',
        'bus_stop_from_hanover',
        'financial_assistance', 'waiver', 'doc_membership',
        'green_fund_donation', 'final_request'
    ]


class RegistrationUpdate(DatabaseEditPermissionRequired,
                         TripsYearMixin, UpdateView):
    """ 
    Edit a registration.
    """
    form_class = RegistrationForm
    model = Registration
    template_name = 'db/update.html'


class RegistrationDelete(DatabaseDeleteView):
    """
    Delete a registration.
    """
    model = Registration
    success_url_pattern = 'db:registration_index'
    

class IncomingStudentIndex(DatabaseReadPermissionRequired,
                           TripsYearMixin, ListView):
    """ 
    All incoming students
    """
    model = IncomingStudent
    template_name = 'incoming/trippee_index.html'
    context_object_name = 'trippees'

    def get_queryset(self):
        qs = super(IncomingStudentIndex, self).get_queryset()
        return qs.select_related(
            'registration__user',
            'registration__bus_stop',
            'trip_assignment__section',
            'trip_assignment__template',
            'bus_assignment_round_trip'
        )


class IncomingStudentDetail(DatabaseDetailView):
    model = IncomingStudent
    template_name = 'incoming/trippee_detail.html'
    context_object_name = 'trippee'

    admin_fields = (
        'registration', 'financial_aid',
        ('total cost', 'compute_cost'),
        'med_info', 'show_med_info',
        'decline_reason', 'notes'
    )
    college_fields = (
        'name', 'netid', 'class_year', 'gender', 'birthday',
        'ethnic_code', 'incoming_status', 'email', 'blitz',
        'phone', 'address'
    )

    def get_context_data(self, **kwargs):
        kwargs['edit_assignment_url'] = reverse(
            'db:incomingstudent_update_assignment', kwargs=self.kwargs
        )
        return super(IncomingStudentDetail, self).get_context_data(**kwargs)


class IncomingStudentDelete(DatabaseDeleteView):
    """ 
    Delete an incoming student.
    """
    model = IncomingStudent

    def get_success_url(self):
        return reverse('db:incomingstudent_index',
                       kwargs={'trips_year': self.get_trips_year()})


class UpdateTripAssignment(DatabaseUpdateView):
    """
    Edit trip and bus assignments for an incoming student.
    """
    model = IncomingStudent
    template_name = 'incoming/update_trip.html'
    form_class = AssignmentForm

    def get_context_data(self, **kwargs):
        reg = self.object.get_registration()
        if reg:
            kwargs['firstchoice_trips'] = reg.get_firstchoice_trips()
            kwargs['preferred_trips'] = reg.get_preferred_trips()
            kwargs['available_trips'] = reg.get_available_trips()
        kwargs['registration'] = reg
        return super(UpdateTripAssignment, self).get_context_data(**kwargs)


class IncomingStudentUpdate(DatabaseUpdateView):
    """
    Edit other incoming student information.
    """
    model = IncomingStudent
    context_object_name = 'trippee'
    form_class = TrippeeInfoForm
    delete_button = False


class UploadIncomingStudentData(DatabaseEditPermissionRequired,
                                TripsYearMixin, FormView):
    """
    Accept an upload of CSV file of incoming students.

    Parses the CSV file and adds the data to the database as
    IncomingStudent objects.

    .. todo:: parse or input the status of the incoming student
    .. todo:: simplify and document the column names
    """
    form_class = UploadIncomingStudentsForm
    template_name = 'incoming/upload_incoming_students.html'

    def form_valid(self, form):

        file = io.TextIOWrapper(
            form.files['csv_file'].file, encoding='utf-8', errors='replace'
        )
        try:
            (ctd, skipped) = IncomingStudent.objects.create_from_csv_file(
                file, self.kwargs['trips_year'])

            if ctd:
                msg = 'Created incoming students with NetIds %s'
                logger.info(msg % ctd)
                messages.info(self.request, msg % ctd)
       
            if skipped:
                msg = 'Ignored existing incoming students with NetIds %s'
                logger.info(msg % skipped)
                messages.warning(self.request, msg % ctd)

        except KeyError as exc:
            msg = "A column is missing (or mis-named) in the uploaded file: %s"
            messages.error(self.request, msg % exc)

        return super(UploadIncomingStudentData, self).form_valid(form)

    def get_success_url(self):
        return self.request.path
       

class MatchRegistrations(DatabaseEditPermissionRequired,
                         TripsYearMixin, FormView):
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
        regs = Registration.objects.filter(trips_year=self.get_trips_year())
        matches = []
        for reg in regs:
            if not hasattr(reg, 'trippee'):
                matches.append(reg.match())
        messages.info(self.request, 'Matched %s' % list(filter(None, matches)))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('db:registration_match', kwargs=self.kwargs)
