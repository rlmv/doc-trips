from vanilla import FormView, DetailView, ListView, CreateView
from django.http import HttpResponseRedirect

from doc.permissions.views import SafetyLogPermissionRequired
from doc.db.views import (
    DatabaseCreateView, DatabaseDetailView, TripsYearMixin,
    DatabaseListView
)
from doc.safety.models import Incident, IncidentUpdate
from doc.safety.forms import IncidentForm, IncidentUpdateForm


class _IncidentMixin(SafetyLogPermissionRequired, TripsYearMixin):
    pass


class IncidentList(_IncidentMixin, ListView):
    model = Incident
    context_object_name = 'incidents'


class NewIncident(_IncidentMixin, CreateView):
    model = Incident

    def get_form(self, **kwargs):
        return IncidentForm(self.kwargs['trips_year'], **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(NewIncident, self).form_valid(form)


class IncidentDetail(_IncidentMixin, FormView, DetailView):
    model = Incident
    template_name = 'safety/detail.html'
    fields = (
        'trip',
        'where',
        'when',
        'caller',
        'caller_role',
        'caller_number',
        'injuries',
        'subject',
        'subject_role',
        'desc',
        'resp',
        'outcome',
        'follow_up'
    )
    update_fields = (
        'caller',
        'caller_role',
        'caller_number',
        'update',
    )
    form_class = IncidentUpdateForm

    def get_context_data(self, **kwargs):
        kwargs[self.get_context_object_name()] = self.get_object()
        return super(IncidentDetail, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.trips_year_id = self.kwargs['trips_year']
        form.instance.user = self.request.user
        form.instance.incident = self.get_object()
        form.save()
        return HttpResponseRedirect(self.request.path)
