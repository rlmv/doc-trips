from collections import defaultdict
from datetime import datetime
from pprint import pprint

from vanilla.views import TemplateView, FormView
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from braces.views import FormValidMessageMixin

from fyt.db.views import (DatabaseCreateView, DatabaseUpdateView,
                          DatabaseDeleteView, DatabaseListView,
                          DatabaseDetailView, DatabaseTemplateView,
                          TripsYearMixin)
from fyt.permissions.views import DatabaseReadPermissionRequired, DatabaseEditPermissionRequired
from fyt.transport.models import (
    Stop, Route, Vehicle, ScheduledTransport, ExternalBus, StopOrder
)
from fyt.transport.maps import MapError
from fyt.transport.forms import StopOrderFormHelper, StopOrderFormset
from fyt.trips.models import Section, Trip
from fyt.utils.matrix import OrderedMatrix
from fyt.utils.views import PopulateMixin
from fyt.utils.cache import cache_as, preload
from fyt.incoming.models import IncomingStudent


NOT_SCHEDULED = 'NOT_SCHEDULED'
EXCEEDS_CAPACITY = 'EXCEEDS_CAPACITY'


def get_internal_route_matrix(trips_year):

    routes = Route.objects.internal(trips_year).select_related('vehicle')
    dates = Section.dates.trip_dates(trips_year)
    matrix = OrderedMatrix(routes, dates)
    scheduled = preload_transported_trips(
        ScheduledTransport.objects.internal(
            trips_year
        ).select_related(
            'route__vehicle'
        ).prefetch_related(
            'stoporder_set'
        ), trips_year
    )
    for transport in scheduled:
        matrix[transport.route][transport.date] = transport

    return matrix


def preload_transported_trips(buses, trips_year):
    """
    Given a qs of internal buses, preload all trips are
    picked up, dropped off, and returned to hanover by
    each bus.
    """
    trips = Trip.objects.with_counts(
        trips_year=trips_year
    ).select_related(
        'dropoff_route',
        'pickup_route',
        'return_route',
        'template__pickup_stop__route',
        'template__dropoff_stop__route',
        'template__return_route',
    )

    dropoffs = defaultdict(lambda: defaultdict(list))
    pickups = defaultdict(lambda: defaultdict(list))
    returns = defaultdict(lambda: defaultdict(list))

    for trip in trips:
        dropoffs[trip.get_dropoff_route()][trip.dropoff_date].append(trip)
        pickups[trip.get_pickup_route()][trip.pickup_date].append(trip)
        returns[trip.get_return_route()][trip.return_date].append(trip)

    for bus in buses:
        preload(bus, bus.DROPOFF_CACHE_NAME, dropoffs[bus.route][bus.date])
        preload(bus, bus.PICKUP_CACHE_NAME, pickups[bus.route][bus.date])
        preload(bus, bus.RETURN_CACHE_NAME, returns[bus.route][bus.date])

    return buses


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
    trips = (
        Trip.objects.with_counts(trips_year)
        .select_related(
            'template', 'section',
            'pickup_route',
            'dropoff_route',
            'return_route',
            'template__dropoff_stop__route',
            'template__pickup_stop__route',
            'template__return_route'
        )
    )
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

    matrix = riders_matrix.map(lambda x: None)  # new matrix w/ null entries

    for route, dates in matrix.items():
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
    template_name = 'transport/internal_matrix.html'

    def get_context_data(self, **kwargs):
        context = super(ScheduledTransportMatrix, self).get_context_data(**kwargs)
        trips_year = self.kwargs['trips_year']
        context['matrix'] = matrix = get_internal_route_matrix(trips_year)
        context['riders'] = riders = get_internal_rider_matrix(trips_year)
        context['issues'] = get_internal_issues_matrix(matrix, riders)
        context['NOT_SCHEDULED'] = NOT_SCHEDULED
        context['EXCEEDS_CAPACITY'] = EXCEEDS_CAPACITY

        # transport count info
        m = get_actual_rider_matrix(trips_year)
        context['dropoff_matrix'] = m.map(lambda x: x.dropping_off).truncate()
        context['pickup_matrix'] = m.map(lambda x: x.picking_up).truncate()
        context['return_matrix'] = m.map(lambda x: x.returning).truncate()

        return context


class ScheduledTransportCreateView(PopulateMixin, DatabaseCreateView):
    model = ScheduledTransport
    fields = ['route', 'date']

    def get_success_url(self):
        return reverse('db:scheduledtransport_index', kwargs=self.kwargs)


class ScheduledTransportUpdateView(DatabaseUpdateView):
    model = ScheduledTransport
    fields = ['notes']
    delete_button = False

    def get_headline(self):
        return "Add notes to %s" % self.object


class ScheduledTransportDeleteView(DatabaseDeleteView):
    model = ScheduledTransport
    success_url_pattern = 'db:scheduledtransport_index'


class ExternalBusCreate(PopulateMixin, DatabaseCreateView):
    model = ExternalBus
    fields = ['route', 'section']

    def get_success_url(self):
        return reverse('db:externalbus_matrix',
                       kwargs={'trips_year': self.kwargs['trips_year']})


class ExternalBusDelete(DatabaseDeleteView):
    model = ExternalBus

    def get_success_url(self):
        return reverse('db:externalbus_matrix',
                       kwargs={'trips_year': self.kwargs['trips_year']})


class ExternalBusMatrix(DatabaseTemplateView):
    template_name = 'transport/external_matrix.html'

    def extra_context(self):
        return {
            'matrix': ExternalBus.objects.schedule_matrix(
                self.kwargs['trips_year']),
            'to_hanover': ExternalBus.passengers.matrix_to_hanover(
                self.kwargs['trips_year']),
            'from_hanover': ExternalBus.passengers.matrix_from_hanover(
                self.kwargs['trips_year'])
        }


class StopListView(DatabaseListView):
    model = Stop
    context_object_name = 'stops'
    template_name = 'transport/stop_index.html'

    def get_queryset(self):
        qs = super(StopListView, self).get_queryset()
        return qs.select_related(
            'route'
        ).order_by(
            'route__category', 'route', 'name'
        )


class StopCreateView(DatabaseCreateView):
    model = Stop


class StopDetailView(DatabaseDetailView):
    model = Stop
    fields = [
        'name', 'address', 'lat_lng',
        'route', 'directions',
        'picked_up_trips', 'dropped_off_trips',
        'cost_round_trip', 'cost_one_way',
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


class _DateMixin():
    """
    Mixin to get a date object from url kwargs.
    """
    def get_date(self):
        """
        Convert from ISO date format
        """
        return datetime.strptime(self.kwargs['date'], "%Y-%m-%d").date()

    def get_context_data(self, **kwargs):
        kwargs['date'] = self.get_date()
        return super(_DateMixin, self).get_context_data(**kwargs)


class _RouteMixin():
    """
    Mixin to get a route object from url kwargs.
    """
    @cache_as('_route')
    def get_route(self):
        return Route.objects.get(pk=self.kwargs['route_pk'])

    def get_context_data(self, **kwargs):
        kwargs['route'] = self.get_route()
        return super(_RouteMixin, self).get_context_data(**kwargs)


class TransportChecklist(_DateMixin, _RouteMixin, DatabaseTemplateView):
    """
    Shows all trips which are supposed to be dropped off,
    picked up, or returned to campus on the date and route
    in the kwargs.
    """
    template_name = 'transport/transport_checklist.html'

    def get_context_data(self, **kwargs):
        context = super(TransportChecklist, self).get_context_data(**kwargs)

        args = (self.get_route(), self.get_date(), self.get_trips_year())
        context['dropoffs'] = Trip.objects.dropoffs(*args)
        context['pickups'] = Trip.objects.pickups(*args)
        context['returns'] = Trip.objects.returns(*args)

        context['scheduled'] = bus = ScheduledTransport.objects.filter(
            trips_year=self.get_trips_year(),
            date=self.get_date(),
            route=self.get_route()
        ).first()

        if bus:
            context['stops'] = bus.get_stops()
            context['over_capacity'] = bus.over_capacity()

        return context


class ExternalBusChecklist(_RouteMixin, DatabaseTemplateView):

    template_name = 'transport/externalbus_checklist.html'

    def get_section(self):
        return Section.objects.get(pk=self.kwargs['section_pk'])

    def extra_context(self):
        return {
            'section': self.get_section(),
            'bus': ExternalBus.objects.filter(
                trips_year=self.get_trips_year(),
                route=self.get_route(), section=self.get_section()
            ).first(),
            'passengers_to_hanover': IncomingStudent.objects.passengers_to_hanover(
                self.get_trips_year(), self.get_route(), self.get_section()),
            'passengers_from_hanover': IncomingStudent.objects.passengers_from_hanover(
                self.get_trips_year(), self.get_route(), self.get_section()),
        }


class OrderStops(DatabaseEditPermissionRequired, TripsYearMixin,
                 FormValidMessageMixin, FormView):
    template_name = 'transport/internal_order.html'
    form_valid_message = 'Route order has been updated'

    def get_queryset(self):
        return self.get_bus().update_stop_ordering()

    @cache_as('_bus')
    def get_bus(self):
        return get_object_or_404(
            ScheduledTransport, pk=self.kwargs['bus_pk'],
            trips_year=self.kwargs['trips_year']
        )

    def get_form(self, **kwargs):
        formset = StopOrderFormset(queryset=self.get_queryset(), **kwargs)
        formset.helper = StopOrderFormHelper()
        return formset

    def form_valid(self, formset):
        formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        kwargs.update({
            'bus': self.get_bus(),
            'checklist_url': self.get_bus().detail_url()
        })
        return super(OrderStops, self).get_context_data(**kwargs)


class InternalBusPacket(DatabaseListView):
    """
    Directions and notes for all internal buses.
    """
    model = ScheduledTransport
    template_name = 'transport/internal_packet.html'
    context_object_name = 'bus_list'


class InternalBusPacketForDate(_DateMixin, InternalBusPacket):
    """
    All internal bus directions for a certain date.
    """
    def get_queryset(self):
        qs = super(InternalBusPacketForDate, self).get_queryset()
        return qs.filter(date=self.get_date())


class ExternalBusPacket(DatabaseListView):
    """
    """
    model = ExternalBus
    template_name = 'transport/external_packet.html'

    TO_HANOVER = 'to Hanover'
    FROM_HANOVER = 'from Hanover'

    def get_queryset(self):
        qs = super(ExternalBusPacket, self).get_queryset()
        return qs.select_related(
            'section',
            'route',
        )

    def get_bus_list(self):
        bus_list = []
        for bus in self.get_queryset():
            bus_list += [
                self.to_hanover_tuple(bus),
                self.from_hanover_tuple(bus)
            ]
        return bus_list

    def extra_context(self):
        # sort by date, then bus name, then direction
        order = {
            self.TO_HANOVER: 0,
            self.FROM_HANOVER: 1
        }
        key = lambda x: (x[0], x[2].route.name, order[x[1]])
        return {
            'bus_list': sorted(self.get_bus_list(), key=key)
        }

    def to_hanover_tuple(self, bus):
        return (bus.date_to_hanover, self.TO_HANOVER, bus)

    def from_hanover_tuple(self, bus):
        return (bus.date_from_hanover, self.FROM_HANOVER, bus)


class ExternalBusPacketForDate(_DateMixin, ExternalBusPacket):
    """
    External bus directions for a certain date.
    """
    def get_bus_list(self):
        bus_list = []
        for bus in self.get_queryset():
            if self.get_date() == bus.date_to_hanover:
                bus_list.append(self.to_hanover_tuple(bus))
            elif self.get_date() == bus.date_from_hanover:
                bus_list.append(self.from_hanover_tuple(bus))
        return bus_list


class ExternalBusPacketForDateAndRoute(_RouteMixin, ExternalBusPacketForDate):
    """
    External bus directions for a date and route
    """
    def get_queryset(self):
        qs = super(ExternalBusPacketForDateAndRoute, self).get_queryset()
        return qs.filter(route=self.get_route())
