
from django.core.urlresolvers import reverse_lazy, reverse
from vanilla import ListView, UpdateView, CreateView, DeleteView

from trip.models import ScheduledTrip
from db.views import DatabaseMixin

class ScheduledTripListView(DatabaseMixin, ListView):
    model = ScheduledTrip
    template_name = 'trip/trip_index.html'
    context_object_name = 'trips'


class ScheduledTripUpdateView(DatabaseMixin, UpdateView):
    model = ScheduledTrip
    template_name = 'db/update.html'


class ScheduledTripCreateView(CreateView):
    model = ScheduledTrip
    template_name = 'db/create.html'


class ScheduledTripDeleteView(DatabaseMixin, DeleteView):

    model = ScheduledTrip
    template_name = 'db/update.html'

    def get_success_url(self):
        kwargs = {'trips_year' : self.kwargs['trips_year']}
        return reverse('db:trip:trip_index', kwargs=kwargs)
    


