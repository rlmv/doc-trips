

from db.views import (DatabaseCreateView, DatabaseUpdateView, DatabaseDeleteView,
                      DatabaseListView, DatabaseDetailView)

from transport.models import Stop, Route, Vehicle


class StopListView(DatabaseListView):
    model = Stop
    context_object_name = 'stops'
    template_name = 'transport/stop_index.html'

class StopCreateView(DatabaseCreateView):
    model = Stop

class StopDetailView(DatabaseDetailView):
    model = Stop
#    fields = ['name', 'address', 'latitude', 'longitude', 'category', 'route']

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
    fields = ['name', 'vehicle', 'category']

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
