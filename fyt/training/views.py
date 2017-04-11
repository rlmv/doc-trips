from django.core.urlresolvers import reverse

from fyt.db.views import DatabaseCreateView, DatabaseListView
from fyt.training.forms import SessionForm
from fyt.training.models import Session


class NewSession(DatabaseCreateView):
    model = Session
    form_class = SessionForm

    def get_headline(self):
        return "Schedule a Training"

    def get_success_url(self):
        kwargs = {'trips_year': self.get_trips_year()}
        return reverse('db:session:list', kwargs=kwargs)


class SessionList(DatabaseListView):
    model = Session
    context_object_name = 'sessions'
