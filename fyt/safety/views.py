from braces.views import SetHeadlineMixin
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from vanilla import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)

from fyt.db.views import TripsYearMixin
from fyt.permissions.views import SafetyLogPermissionRequired
from fyt.safety.forms import IncidentForm, IncidentUpdateForm
from fyt.safety.models import Incident
from fyt.utils.forms import crispify


class _IncidentMixin(SafetyLogPermissionRequired, TripsYearMixin):
    pass


class IncidentList(_IncidentMixin, ListView):
    model = Incident
    context_object_name = 'incidents'


class NewIncident(_IncidentMixin, SetHeadlineMixin, CreateView):
    model = Incident
    template_name = 'db/create.html'
    headline = 'New Incident'

    def get_form(self, **kwargs):
        return IncidentForm(self.kwargs['trips_year'], **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.trips_year_id = self.kwargs['trips_year']
        return super().form_valid(form)


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
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.trips_year_id = self.kwargs['trips_year']
        form.instance.user = self.request.user
        form.instance.incident = self.get_object()
        form.save()
        return HttpResponseRedirect(self.request.path)


class DeleteIncident(_IncidentMixin, SetHeadlineMixin, DeleteView):
    model = Incident
    template_name = 'db/delete.html'

    def get_headline(self):
        return ("Are you sure you want to delete Incident %s? "
                "You will not be able to undo this." % self.object)

    def get_success_url(self):
        return reverse('db:safety:list', kwargs={
            'trips_year': self.kwargs['trips_year']
        })

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        messages.success(request, "Deleted Incident %s" % self.object)
        return resp


class UpdateIncident(_IncidentMixin, UpdateView):
    model = Incident
    template_name = 'db/update.html'
    fields = ['status']

    def get_form(self, **kwargs):
        return crispify(super().get_form(**kwargs))
