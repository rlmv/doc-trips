import logging

from braces.views import SetHeadlineMixin
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from vanilla import FormView, UpdateView

from fyt.applications.models import Volunteer
from fyt.db.models import TripsYear
from fyt.db.views import (
    DatabaseCreateView, DatabaseDetailView, DatabaseListView,
    DatabaseUpdateView, DatabaseDeleteView)
from fyt.training.forms import SessionForm, SignupForm
from fyt.training.models import Attendee, Session
from fyt.utils.forms import crispify


log = logging.getLogger(__name__)


class NewSession(DatabaseCreateView):
    model = Session
    form_class = SessionForm

    def get_headline(self):
        return "Schedule a Training"


class SessionList(DatabaseListView):
    model = Session
    context_object_name = 'sessions'


class SessionDetail(DatabaseDetailView):
    model = Session
    fields = [
        'time',
        'duration',
        ('registered', 'attendee_set'),
        ('emails', 'attendee_emails_str')
    ]


class SessionUpdate(DatabaseUpdateView):
    model = Session
    form_class = SessionForm


class SessionDelete(DatabaseDeleteView):
    model = Session


# Volunteer-facing views

class Signup(SetHeadlineMixin, UpdateView):

    model = Attendee
    form_class = SignupForm
    template_name = 'form.html'

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

    def get_headline(self):
        return "Signup for training sessions"

    def get_success_url(self):
        return self.request.path
