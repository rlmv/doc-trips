import logging

from braces.views import FormMessagesMixin, SetHeadlineMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from vanilla import FormView, UpdateView

from fyt.applications.models import Volunteer
from fyt.db.models import TripsYear
from fyt.db.views import (
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
    AttendeeUpdateForm,
    FirstAidFormset,
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
        'completed'
    ]

    def extra_context(self):
        return {
            'update_attendance_url': reverse(
                'db:session:update_attendance',
                kwargs=self.object.obj_kwargs()),
            'update_registration_url': reverse(
                'db:session:update_registration',
                kwargs=self.object.obj_kwargs()),
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
        return mark_safe(
            "Record Attendance <small>{}</small>".format(self.object))

    def has_permission(self):
        """Directorate members can also update training attendance."""
        return super().has_permission() or (
            groups.directorate in self.request.user.groups.all())


class UpdateRegistration(TrainingPermissionRequired, BaseUpdateView):
    model = Session
    form_class = SessionRegistrationForm
    delete_button = False

    def get_headline(self):
        return mark_safe(
            "Update Registrations <small>{}</small>".format(self.object))


class RecordFirstAid(TrainingPermissionRequired, SetHeadlineMixin,
                     TripsYearMixin, FormView):
    """
    Batch update first aid certifications.
    """
    template_name = 'db/form.html'

    def get_headline(self):
        return 'First Aid Certifications'

    def get_form(self, **kwargs):
        return FirstAidFormset(trips_year=self.get_trips_year(), **kwargs)

    def form_valid(self, formset):
        formset.save()
        return super().form_valid(formset)

    def get_success_url(self):
        return self.request.path


class AttendeeUpdate(TrainingPermissionRequired, BaseUpdateView):
    model = Attendee
    delete_button = False
    form_class = AttendeeUpdateForm


# Volunteer-facing views

class Signup(LoginRequiredMixin, UserPassesTestMixin, FormMessagesMixin,
             UpdateView):

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

        return attendee.can_register

    def get_object(self):
       return Attendee.objects.get(
            trips_year=self.get_trips_year(),
            volunteer__applicant=self.request.user)

    def get_trips_year(self):
        return TripsYear.objects.current()

    def get_form(self, *args, **kwargs):
        return crispify(super().get_form(*args, **kwargs))

    def get_success_url(self):
        return self.request.path
