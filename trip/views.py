

from vanilla import ListView, UpdateView, CreateView

from trip.models import ScheduledTrip
from db.views import DatabaseMixin

class ScheduledTripListView(DatabaseMixin, ListView):
    model = ScheduledTrip
    template_name = 'trip/trip_index.html'
    context_object_name = 'trips'


class ScheduledTripUpdateView(DatabaseMixin, UpdateView):
    model = ScheduledTrip
    template_name = 'db/update.html'
    context_object_name = 'trip'

class ScheduledTripCreateView(CreateView):
    model = ScheduledTrip
    template_name = 'db/create.html'


