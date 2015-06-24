from collections import namedtuple
from datetime import datetime

from vanilla.views import TemplateView
from django.core.urlresolvers import reverse

from doc.db.views import (DatabaseCreateView, DatabaseUpdateView,
                          DatabaseDeleteView, DatabaseListView,
                          DatabaseDetailView, TripsYearMixin)
from doc.permissions.views import DatabaseReadPermissionRequired
from doc.transport.models import (
    Stop, Route, Vehicle, ScheduledTransport, ExternalTransport)
from doc.trips.models import Section, ScheduledTrip
from doc.utils.matrix import OrderedMatrix

NOT_SCHEDULED = 'NOT_SCHEDULED'
EXCEEDS_CAPACITY = 'EXCEEDS_CAPACITY'

def get_internal_route_matrix(trips_year):

    routes = (Route.objects.internal(trips_year)
              .select_related('vehicle'))
    dates = Section.dates.trip_dates(trips_year)
   
    matrix = {route: {date: None for date in dates} for route in routes}
    scheduled = (ScheduledTransport.objects.internal(trips_year)
                 .select_related('route'))
    for transport in scheduled:
        matrix[transport.route][transport.date] = transport

    return matrix


class Riders:
    """ 
    Utility class to represent the number of riders on a route.
    
    Riders objects can be added to each other. An empty Riders object 
    evaluates to False for convenience.

    TODO: "Riders" doesn't really mean much, semantically.
    """

    def __init__(self, dropping_off, picking_up, returning):
        self.dropping_off = dropping_off
        self.picking_up = picking_up
        self.returning = returning

    def __add__(self, y):
        d = self.dropping_off + y.dropping_off
        p = self.picking_up + y.picking_up
        r = self.returning + y.returning
        return Riders(d, p, r)

    def __bool__(self):
        return bool(self.dropping_off or self.picking_up or self.returning)

    def __eq__(self, y):
        return (self.dropping_off == y.dropping_off and
                self.picking_up == y.picking_up and
                self.returning == y.returning)

    def __ne__(self, y):
        return not self.__eq__(y)

    def __str__(self):
        return "Dropping off {}, picking up {}, returning {} to campus".format(
            self.dropping_off, self.picking_up, self.returning
        )

    __repr__ = __str__


def get_internal_rider_matrix(trips_year):
    """
    Matrix of hypothetical numbers, 
    computed with max_trippees + 2 leaders.
    
    matrix[route][date] gives you the Riders for that route on that date.
    """
  
    return _rider_matrix(trips_year, lambda trip: trip.template.max_num_people)


def get_actual_rider_matrix(trips_year):
    """ 
    Matrix of actual, assigned transport numbers.
    """
    return _rider_matrix(trips_year, lambda trip: trip.size())


def _rider_matrix(trips_year, size_key):
    """
    Size key computes the number of riders on a transport leg
    """

    routes = Route.objects.internal(trips_year)
    dates = Section.dates.trip_dates(trips_year)
    trips = (ScheduledTrip.objects.filter(trips_year=trips_year)
             .select_related('template', 'section', 'template__dropoff__route',
                             'template__pickup__route', 'template__return_route'))
      
    matrix = OrderedMatrix(routes, dates, lambda: Riders(0, 0, 0))

    for trip in trips:

        n = size_key(trip)
        # dropoff 
        if trip.get_dropoff_route():
            matrix[trip.get_dropoff_route()][trip.dropoff_date] += Riders(n, 0, 0)
        # pickup
        if trip.get_pickup_route():
            matrix[trip.get_pickup_route()][trip.pickup_date] += Riders(0, n, 0)
        # return 
        matrix[trip.get_return_route()][trip.return_date] += Riders(0, 0, n)
        
    return matrix


def get_internal_issues_matrix(transport_matrix, riders_matrix):

    assert len(transport_matrix.keys()) == len(riders_matrix.keys())

    dates = transport_matrix[next(iter(transport_matrix))].keys()
    matrix = {route: {date: None for date in dates} for route in transport_matrix.keys()}
    for route in matrix.keys():
        for date in dates:
            transport = transport_matrix[route][date]
            riders = riders_matrix[route][date]
            capacity = route.vehicle.capacity
            if riders and not transport:
                matrix[route][date] = NOT_SCHEDULED
            elif riders and (riders.dropping_off > capacity or 
                             riders.picking_up > capacity or
                             riders.returning > capacity):
                matrix[route][date] = EXCEEDS_CAPACITY

    return matrix

class ScheduledTransportMatrix(DatabaseReadPermissionRequired,
                               TripsYearMixin, TemplateView):
    template_name = 'transport/transport_list.html'

    def get_context_data(self, **kwargs):
        context = super(ScheduledTransportMatrix, self).get_context_data(**kwargs)
        trips_year = self.kwargs['trips_year']
        context['matrix'] = matrix = get_internal_route_matrix(trips_year)
        context['dates'] = sorted(matrix[next(iter(matrix))].keys())  # dates in matrix
        context['riders'] = riders = get_internal_rider_matrix(trips_year)
        context['issues'] = get_internal_issues_matrix(matrix, riders)
        context['NOT_SCHEDULED'] = NOT_SCHEDULED
        context['EXCEEDS_CAPACITY'] = EXCEEDS_CAPACITY
        return context


class TransportCounts(DatabaseReadPermissionRequired,
                      TripsYearMixin, TemplateView):
    template_name = 'transport/transport_counts.html'

    def get_context_data(self, **kwargs):
        context = super(TransportCounts, self).get_context_data(**kwargs)
        m = get_actual_rider_matrix(self.kwargs['trips_year'])
        context['dropoff_matrix'] = m.map(lambda x: x.dropping_off).truncate()
        context['pickup_matrix'] = m.map(lambda x: x.picking_up).truncate()
        context['return_matrix'] = m.map(lambda x: x.returning).truncate()
        return context


class ScheduledTransportCreateView(DatabaseCreateView):
    
    model = ScheduledTransport
    fields = ('route', 'date')
    
    def get_success_url(self):
        return reverse('db:scheduledtransport_index', kwargs=self.kwargs)

    def get(self, request, *args, **kwargs):
        
        data = None
        GET = request.GET
        if 'route' in GET and 'date' in GET:
            data = {'route': GET['route'], 'date': GET['date']}

        form = self.get_form(data=data)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class ScheduledTransportDeleteView(DatabaseDeleteView):
    model = ScheduledTransport
    success_url_pattern = 'db:scheduledtransport_index'


class PopulateMixin():
    
    def get(self, request, *args, **kwargs):
        """
        Populate the create form with data passed 
        in the url querystring.
        """
        data = request.GET or None
        form = self.get_form(data=data)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class ExternalTransportCreate(PopulateMixin, DatabaseCreateView):
    model = ExternalTransport
    fields = ['route', 'section']

    def get_success_url(self):
        return reverse('db:externaltransport_matrix',
                       kwargs={'trips_year': self.kwargs['trips_year']})


class ExternalTransportDelete(DatabaseDeleteView):
    model = ExternalTransport
    
    def get_success_url(self):
        return reverse('db:externaltransport_matrix',
                       kwargs={'trips_year': self.kwargs['trips_year']})


class ExternalTransportMatrix(DatabaseReadPermissionRequired,
                              TripsYearMixin, TemplateView):

    template_name = 'transport/external_matrix.html'

    def get_context_data(self, **kwargs):
        kwargs['matrix'] = ExternalTransport.objects.schedule_matrix(
            self.kwargs['trips_year']
        )
        return super(ExternalTransportMatrix, self).get_context_data(**kwargs)


class StopListView(DatabaseListView):
    model = Stop
    context_object_name = 'stops'
    template_name = 'transport/stop_index.html'

    def get_queryset(self):
        qs = super(StopListView, self).get_queryset()
        return qs.select_related('route')


class StopCreateView(DatabaseCreateView):
    model = Stop


class StopDetailView(DatabaseDetailView):
    model = Stop
    fields = [
        'name', 'address', 'route', 'directions',
        'picked_up_trips', 'dropped_off_trips',
        'latitude', 'longitude', 'cost',
        'pickup_time', 'dropoff_time', 'distance',    
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


class TransportChecklist(DatabaseReadPermissionRequired,
                         TripsYearMixin, TemplateView):
    """ 
    Shows all trips which are supposed to be dropped off,
    picked up, or returned to campus on the date and route
    in the kwargs.
    """

    template_name = 'transport/transport_checklist.html'

    def get_date(self):
        """ Convert from ISO date format """
        return datetime.strptime(self.kwargs['date'], "%Y-%m-%d").date()

    def get_route(self):
        return Route.objects.get(pk=self.kwargs['route_pk'])

    def get_context_data(self, **kwargs):
        context = super(TransportChecklist, self).get_context_data(**kwargs)
        context['route'] = self.get_route()
        context['date'] = self.get_date()

        rel = lambda qs: qs.select_related('section', 'template')
        args = (self.get_route(), self.get_date(), self.get_trips_year())
        context['dropoffs'] = rel(ScheduledTrip.objects.dropoffs(*args))
        context['pickups'] = rel(ScheduledTrip.objects.pickups(*args))
        context['returns'] = rel(ScheduledTrip.objects.returns(*args))
      
        return context
        
