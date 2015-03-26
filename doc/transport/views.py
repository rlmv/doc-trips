
from vanilla.views import TemplateView

from doc.db.views import (DatabaseCreateView, DatabaseUpdateView,
                          DatabaseDeleteView, DatabaseListView,
                          DatabaseDetailView, TripsYearMixin)
from doc.permissions.views import DatabaseReadPermissionRequired
from doc.transport.models import Stop, Route, Vehicle, ScheduledTransport
from doc.trips.models import Section


def get_internal_route_matrix(trips_year):

    routes = Route.objects.internal(trips_year)
    dates = Section.dates.trip_dates(trips_year)
   
    matrix = {route: {date: None for date in dates} for route in routes}
    scheduled = ScheduledTransport.objects.internal(trips_year)
    for transport in scheduled:
        matrix[transport.route][transport.date] = transport

    return matrix


class ScheduledTransportMatrix(DatabaseReadPermissionRequired,
                               TripsYearMixin, TemplateView):
    template_name = 'transport/transport_list.html'

    def get_context_data(self, **kwargs):
        context = super(ScheduledTransportMatrix, self).get_context_data(**kwargs)
        trips_year = self.kwargs['trips_year']
        matrix = get_internal_route_matrix(trips_year)
        context['matrix'] = matrix
        context['dates'] = matrix[list(matrix.keys())[0]].keys() #  dates in matrix
        return context
   

class StopListView(DatabaseListView):
    model = Stop
    context_object_name = 'stops'
    template_name = 'transport/stop_index.html'


class StopCreateView(DatabaseCreateView):
    model = Stop


class StopDetailView(DatabaseDetailView):
    model = Stop
    fields = [
        'name', 'address', 'route', 'directions',
        'latitude', 'longitude', 'cost',
        'pickup_time', 'dropoff_time', 'distance'
    ]


class StopUpdateView(DatabaseUpdateView):
    model = Stop


class StopDeleteView(DatabaseDeleteView):
    model = Stop
    success_url_pattern = 'db:stop_index'


class RouteListView(DatabaseListView):
    model = Route
    context_object_name = 'routes'
    template_name = 'transport/route_index.html'


class RouteCreateView(DatabaseCreateView):
    model = Route


class RouteDetailView(DatabaseDetailView):
    model = Route
    fields = ['name', 'vehicle', 'category', 'stops']


class RouteUpdateView(DatabaseUpdateView):
    model = Route


class RouteDeleteView(DatabaseDeleteView):
    model = Route
    success_url_pattern = 'db:route_index'


class VehicleListView(DatabaseListView):
    model = Vehicle
    context_object_name = 'vehicles'
    template_name = 'transport/vehicle_index.html'


class VehicleCreateView(DatabaseCreateView):
    model = Vehicle


class VehicleDetailView(DatabaseDetailView):
    model = Vehicle
    fields = ['name', 'capacity']


class VehicleUpdateView(DatabaseUpdateView):
    model = Vehicle


class VehicleDeleteView(DatabaseDeleteView):
    model = Vehicle
    success_url_pattern = 'db:vehicle_index'
