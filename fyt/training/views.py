import logging

from braces.views import FormMessagesMixin, SetHeadlineMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from vanilla import ListView, UpdateView

from fyt.applications.models import Volunteer
from fyt.core.models import TripsYear
from fyt.core.views import (
    BaseCreateView,
    BaseDeleteView,
    BaseUpdateView,
    DatabaseCreateView,
    DatabaseDeleteView,
    DatabaseDetailView,
    DatabaseListView,
    TripsYearMixin,
)
from fyt.permissions.permissions import groups
from fyt.permissions.views import TrainingPermissionRequired
from fyt.training.forms import (
    AttendanceForm,
    CompletedSessionsForm,
    FirstAidVerificationFormset,
    SessionForm,
    SessionRegistrationForm,
    SignupForm,
)
from fyt.training.models import Attendee, Session
from fyt.utils.forms import crispify


log = logging.getLogger(__name__)


class NewSession(TrainingPermissionRequired, BaseCreateView):
    model = Session
    form_class = SessionForm

    def get_headline(self):
        return "Schedule a Training"


class SessionList(DatabaseListView):
    model = Session
    context_object_name = 'sessions'


class SessionDetail(DatabaseDetailView):
    model = Session
    template_name = 'training/session_detail.html'
    fields = [
        'date',
        'start_time',
        'end_time',
        'location',
        ('number registered', 'size'),
        'registered',
        ('registered emails', 'registered_emails_str'),
        'completed',
    ]

    def extra_context(self):
        return {
            'update_attendance_url': reverse(
                'core:session:update_attendance', kwargs=self.object.obj_kwargs()
            ),
            'update_registration_url': reverse(
                'core:session:update_registration', kwargs=self.object.obj_kwargs()
            ),
        }


class SessionUpdate(TrainingPermissionRequired, BaseUpdateView):
    model = Session
    form_class = SessionForm


class SessionDelete(TrainingPermissionRequired, BaseDeleteView):
    model = Session

    def get_success_url(self):
        return self.object.index_url()


class RecordAttendance(TrainingPermissionRequired, BaseUpdateView):
    model = Session
    form_class = AttendanceForm
    delete_button = False

    def get_headline(self):
        return mark_safe("Record Attendance <small>{}</small>".format(self.object))


class UpdateRegistration(TrainingPermissionRequired, BaseUpdateView):
    model = Session
    form_class = SessionRegistrationForm
    delete_button = False

    def get_headline(self):
        return mark_safe("Update Registrations <small>{}</small>".format(self.object))


class RecordFirstAid(TrainingPermissionRequired, TripsYearMixin, ListView):
    """
    Batch update first aid certifications.
    """

    template_name = 'training/first_aid_certification_list.html'
    model = Volunteer

    def get_queryset(self):
        return (
            Attendee.objects.trainable(self.trips_year)
            .select_related('volunteer')
            .prefetch_related('volunteer__first_aid_certifications')
        )


class AttendeeSessionsUpdate(TrainingPermissionRequired, BaseUpdateView):
    model = Attendee
    delete_button = False
    form_class = CompletedSessionsForm

    def get_headline(self):
        return mark_safe('Update trainings <small>{}</small>'.format(self.object))


class VolunteerFirstAidUpdate(
    TrainingPermissionRequired, FormMessagesMixin, BaseUpdateView
):
    model = Volunteer
    delete_button = False
    form_class = FirstAidVerificationFormset

    def get_headline(self):
        return mark_safe(
            'Edit First Aid Certifications <small>{}</small>'.format(self.object)
        )

    def get_success_url(self):
        if 'next' in self.request.GET:
            return self.request.GET['next']
        return self.get_object().detail_url()

    def get_form_valid_message(self):
        return "Saved first aid certifications for {}".format(self.get_object())


# Volunteer-facing views


class Signup(LoginRequiredMixin, UserPassesTestMixin, FormMessagesMixin, UpdateView):

    model = Attendee
    form_class = SignupForm
    template_name = 'training/signup_form.html'
    raise_exception = True
    permission_denied_message = "You are not a Leader or a Croo Member."
    form_valid_message = "Your training sessions have been updated"
    form_invalid_message = "There's an issue with the sessions you've choosen"

    def test_func(self):
        """Check whether the user can register for trainings."""
        try:
            attendee = self.get_object()
        except Attendee.DoesNotExist:
            return False

        return attendee.can_register or self.request.user.is_superuser

    def get_object(self):
        return Attendee.objects.get(
            trips_year=self.trips_year, volunteer__applicant=self.request.user
        )

    @cached_property
    def trips_year(self):
        return TripsYear.objects.current()

    def get_form(self, *args, **kwargs):
        return crispify(super().get_form(*args, **kwargs))

    def get_success_url(self):
        return self.request.path
