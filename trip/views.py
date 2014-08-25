

from vanilla import ListView, UpdateView

from trip.models import ScheduledTrip

class ScheduledTripListView(ListView):
    model = ScheduledTrip
    template_name = 'trip/trip_index.html'
    context_object_name = 'trips'

trip_index = ScheduledTripListView.as_view()

class ScheduledTripUpdateView(UpdateView):
    model = ScheduledTrip
    template_name = 'trip/trip_update.html'
    context_object_name = 'trip'

trip_update = ScheduledTripUpdateView.as_view()


