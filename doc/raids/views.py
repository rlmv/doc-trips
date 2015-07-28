from braces.views import LoginRequiredMixin
from vanilla import ListView, DetailView, CreateView

from doc.db.views import TripsYearMixin
from doc.raids.models import Raid
from doc.trips.models import Trip
from doc.utils.views import PopulateMixin
from doc.utils.forms import crispify


class _RaidMixin(LoginRequiredMixin, TripsYearMixin):
    pass


class RaidIndex(_RaidMixin, ListView):
    model = Raid


class TripsToRaid(_RaidMixin, ListView):
    model = Trip
    template_name = 'raids/trips.html'

    def get_queryset(self):
        qs = super(TripsToRaid, self).get_queryset()
        return qs.select_related(
            'template__campsite1',
            'template__campsite2',
        ).prefetch_related(
            'raid_set'
        )


class RaidTrip(_RaidMixin, PopulateMixin, CreateView):
    model = Raid
    fields = ['trip', 'date', 'plan']

    def get_form(self, **kwargs):
        return crispify(super(RaidTrip, self).get_form(**kwargs))

    def form_valid(self, form):
        form.instance.trips_year_id = self.kwargs['trips_year']
        form.instance.user = self.request.user
        return super(RaidTrip, self).form_valid(form)

    def get_success_url(self):
        return self.object.detail_url()


class RaidDetail(_RaidMixin, DetailView):
    model = Raid
