

from doc.db.views import DatabaseCreateView, DatabaseDetailView
from doc.safety.models import Incident
from doc.safety.forms import IncidentForm


class NewIncident(DatabaseCreateView):
    model = Incident

    def get_form(self, **kwargs):
        return IncidentForm(self.kwargs['trips_year'], **kwargs)
        
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(NewIncident, self).form_valid(form)
        

class IncidentDetail(DatabaseDetailView):
    model = Incident
