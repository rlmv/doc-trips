import logging

from braces.views import SetHeadlineMixin
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from vanilla import FormView, UpdateView

from fyt.applications.models import Volunteer
from fyt.db.models import TripsYear
from fyt.db.views import (
    BaseCreateView, BaseUpdateView, BaseDeleteView,
    DatabaseCreateView, DatabaseDetailView, DatabaseListView,
    DatabaseUpdateView, DatabaseDeleteView)
from fyt.permissions.views import TrainingPermissionRequired
from fyt.permissions.permissions import directorate
from fyt.training.forms import AttendanceForm, SessionForm, SignupForm
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
        'registered',
        ('registered emails', 'registered_emails_str'),
        'completed'
    ]

    def extra_context(self):
        return {
            'update_attendance_url': reverse(
                'db:session:update_attendance',
                kwargs=self.object.obj_kwargs())
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

    def get_headline(self):
        return mark_safe(
            "Record Attendance <small>{}</small>".format(self.object))

    def has_permission(self):
        """Directorate members can also update training attendance."""
        return super().has_permission() or (
            directorate() in self.request.user.groups.all())


# Volunteer-facing views

def trainings_available(volunteer):
    allowed = [Volunteer.LEADER,
               Volunteer.CROO,
               Volunteer.LEADER_WAITLIST]
    return volunteer.status in allowed


class CanRegister(LoginRequiredMixin, UserPassesTestMixin):
    """Check if the Volunteer can register for trainings."""
    raise_exception = True
    permission_denied_message = "You are not a Leader or a Croo Member."

    def test_func(self):
        try:
            volunteer = Volunteer.objects.get(
                trips_year=TripsYear.objects.current(),
                applicant=self.request.user)
        except Volunteer.DoesNotExist:
            return False

        return trainings_available(volunteer)


class Signup(CanRegister, UpdateView):

    model = Attendee
    form_class = SignupForm
    template_name = 'training/signup_form.html'

    # TODO: don't 404; tell user that they aren't a volunteer.
    # TODO: don't create Attendee in GET requests
    def get_object(self):
        volunteer = Volunteer.objects.get(
            trips_year=self.get_trips_year(),
            applicant=self.request.user)

        attendee, created = Attendee.objects.get_or_create(
            volunteer=volunteer,
            trips_year=self.get_trips_year())

        if created:
            log.info('Creating new {}'.format(attendee))

        return attendee

    def get_trips_year(self):
        return TripsYear.objects.current()

    def get_form(self, *args, **kwargs):
        return crispify(super().get_form(*args, **kwargs))

    def get_success_url(self):
        return self.request.path
