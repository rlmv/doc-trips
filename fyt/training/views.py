from django.core.urlresolvers import reverse

from fyt.db.views import (
    DatabaseCreateView, DatabaseDetailView, DatabaseListView,
    DatabaseUpdateView, DatabaseDeleteView)
from fyt.training.forms import SessionForm
from fyt.training.models import Session


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
    ]


class SessionUpdate(DatabaseUpdateView):
    model = Session
    form_class = SessionForm


class SessionDelete(DatabaseDeleteView):
    model = Session
