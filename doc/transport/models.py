from collections import defaultdict

from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from doc.db.models import DatabaseModel
from doc.transport.managers import (
    StopManager, RouteManager, ScheduledTransportManager,
    ExternalBusManager, ExternalPassengerManager, 
    StopOrderManager
)
from doc.transport.maps import get_directions
from doc.utils.lat_lng import validate_lat_lng
from doc.utils.cache import cache_as


class Stop(DatabaseModel):
    """
    A stop on a transportation route.

    Represents a pickup or dropoff point for a trip OR a
    bus stop where local sections are picked up.
    """
    class Meta:
        ordering = ['route__category', 'route', 'name']

    objects = StopManager()

    name = models.CharField(max_length=255)
    address = models.CharField(
        max_length=255, blank=True, default='', help_text=(
            "Plain text address, eg. Hanover, NH 03755. This must "
            "take you to the location in Google maps."
        )
    )
    lat_lng = models.CharField(
        'coordinates', max_length=255, blank=True, default='',
        validators=[validate_lat_lng], help_text=(
            "Latitude & longitude coordinates, eg. 43.7030,-72.2895"
        )
    )
   
    # verbal directions, descriptions. migrated from legacy.
    directions = models.TextField(blank=True)

    route = models.ForeignKey(
        'Route', null=True, blank=True,
        on_delete=models.PROTECT, related_name='stops',
        help_text="default bus route",
    )

    # costs are required for EXTERNAL stops
    cost_round_trip = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        help_text="for external buses"
    )
    cost_one_way = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        help_text="for external buses"
    )

    # mostly used for external routes
    dropoff_time = models.TimeField(blank=True, null=True)
    pickup_time = models.TimeField(blank=True, null=True)
    distance = models.IntegerField(help_text=(
        "this rough distance from Hanover is used for bus routing"
    ))

    def clean(self):
        if not self.lat_lng and not self.address:
            raise ValidationError(
                "%s must set either lat_lng or address" % self)

        if self.category == Route.EXTERNAL:
            if not self.cost_round_trip:
                raise ValidationError("%s requires round-trip cost" % self)
            if not self.cost_one_way:
                raise ValidationError("%s requires one-way cost" % self)

        elif self.category == Route.INTERNAL:
            if self.cost_round_trip or self.cost_one_way:
                raise ValidationError("internal stop cannot have cost")

    @property
    def category(self):
        """
        Either INTERNAL or EXTERNAL
        """
        return self.route.category

    @property
    def location(self):
        """
        Get the location of the stop. Coordinates are
        probably more accurate so we return them if possible.
        """
        if self.lat_lng:
            return self.lat_lng
        return self.address

    def detail_url(self):
        return reverse('db:stop_detail', kwargs=self.obj_kwargs())

    def __str__(self):
        return self.name

    def location_str(self):
        return "%s (%s)" % (self.name, self.location)


class Route(DatabaseModel):
    """
    A transportation route. This is essentially a template for bus
    routes which identifies stops that the same bus should pick
    up.

    A route is either INTERNAL (transporting students to/from Hanover,
    trip dropoffs/pickups, and the lodge) or EXTERNAl (moving local
    students to and from campus before and after their trips.)
    """
    name = models.CharField(max_length=255)
    INTERNAL = 'INTERNAL'
    EXTERNAL = 'EXTERNAL'
    category = models.CharField(
        max_length=20, choices=(
            (INTERNAL, 'Internal'),
            (EXTERNAL, 'External'),
        )
    )
    vehicle = models.ForeignKey('Vehicle', on_delete=models.PROTECT)

    objects = RouteManager()

    class Meta:
        ordering = ['category', 'vehicle', 'name']

    def __str__(self):
        return self.name


class Vehicle(DatabaseModel):
    """
    A type of vehicle
    """
    # eg. Internal Bus, Microbus,
    name = models.CharField(max_length=255)
    capacity = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ScheduledTransport(DatabaseModel):
    """
    Represents a scheduled internal transport.
    """
    objects = ScheduledTransportManager()

    route = models.ForeignKey(Route, on_delete=models.PROTECT)
    date = models.DateField()
    notes = models.TextField(help_text='for the bus driver')

    class Meta:
        unique_together = ['trips_year', 'route', 'date']
        ordering = ['date']

    def clean(self):
        if self.route.category == Route.EXTERNAL:
            raise ValidationError("route must be internal")

    # TODO: move the main implementation of the trip methods to here?
    # We could just instantiate a transport object without saving and
    # call the methods on it.

    @cache_as('_dropping_off')
    def dropping_off(self):
        """
        All trips which this transport drops off (on the trip's day 2)
        """
        from doc.trips.models import Trip
        return (
            Trip.objects
            .dropoffs(self.route, self.date, self.trips_year_id)
            .select_related('template__dropoff_stop')
        )

    @cache_as('_picking_up')
    def picking_up(self):
        """
        All trips which this transport picks up (on trip's day 4)
        """
        from doc.trips.models import Trip
        return (
            Trip.objects
            .pickups(self.route, self.date, self.trips_year_id)
            .select_related('template__pickup_stop')
        )

    @cache_as('_returning')
    def returning(self):
        """
        All trips which this transport returns to Hanover (on day 5)
        """
        from doc.trips.models import Trip
        return (
            Trip.objects
            .returns(self.route, self.date, self.trips_year_id)
        )

    def all_stops(self):
        return set(
            list(map(lambda x: x.template.pickup_stop, self.picking_up())) +
            list(map(lambda x: x.template.dropoff_stop, self.dropping_off()))
        )
        
    @cache_as('_get_stops')
    def get_stops(self):
        """
        All stops which the bus makes as it drops trips off
        and picks them up. The first stop is Hanover, the last
        is the Lodge. Intermediate stops are ordered by their
        distance from Hanover.

        Each stop has a trips_dropped_off and trips_picked_up
        property added to it (TODO: change these names; they 
        conflict with the triptemplate related_names.)
        The properties contain the list of trips which are dropped
        off and picked up at this stop by this bus.
        """
        from doc.transport.constants import Hanover, Lodge

        DROPOFF_ATTR = 'trips_dropped_off'
        PICKUP_ATTR = 'trips_picked_up'

        def set_trip_attr(stop, order):
            for attr in [DROPOFF_ATTR, PICKUP_ATTR]:
                if not hasattr(stop, attr):
                    setattr(stop, attr, [])
              
            if order.stop_type == StopOrder.DROPOFF:
                getattr(stop, DROPOFF_ATTR).append(order.trip)

            if order.stop_type == StopOrder.PICKUP:
                getattr(stop, PICKUP_ATTR).append(order.trip)

            return stop
                
        stops = []
        for order in self.update_stop_ordering():
            if len(stops) == 0 or stops[-1] != order.stop:  # new stop
                stops.append(set_trip_attr(order.stop, order))
            else:  # another trip for the same stop
                set_trip_attr(stops[-1], order)

        # all buses start from Hanover
        hanover = Hanover()
        setattr(hanover, PICKUP_ATTR, list(self.dropping_off()))
        setattr(hanover, DROPOFF_ATTR, [])
        stops = [hanover] + stops

        if self.picking_up() or self.returning():
            # otherwise we can bypass the lodge
            lodge = Lodge()
            setattr(lodge, DROPOFF_ATTR, list(self.picking_up()))
            setattr(lodge, PICKUP_ATTR, list(self.returning()))
            stops.append(lodge)

        if self.returning():
            # take trips back to Hanover
            hanover = Hanover()
            setattr(hanover, DROPOFF_ATTR, list(self.returning()))
            setattr(hanover, PICKUP_ATTR, [])
            stops.append(hanover)

        return stops

    def update_stop_ordering(self):
        """
        Update the ordering of all stops this bus makes.
        Create any missing StopOrder objects, and delete 
        extra objects.

        (Yes, using this in GET requests is poor http semantics,
        but there are more corner cases of when routes change than 
        I want to deal with using signals.)

        Returns a list of StopOrders for each stop that this bus is
        making (excluding Hanover and the Lodge).
        """
        
        opts = (
            (StopOrder.PICKUP, self.picking_up(),
             lambda x: x.template.pickup_stop),
            (StopOrder.DROPOFF, self.dropping_off(),
             lambda x: x.template.dropoff_stop)
        )

        for stop_type, trips, getter in opts:
            ordered_trips = set([x.trip for x in self.stoporder_set.filter(stop_type=stop_type)])
            unordered_trips = set(trips) - ordered_trips
            surplus_trips = ordered_trips - set(trips)

            if unordered_trips:
                # we are missing some ordering objects
                for trip in unordered_trips:
                    StopOrder.objects.create(
                        order=getter(trip).distance,
                        bus=self, trip=trip,
                        trips_year_id=self.trips_year_id,
                        stop_type=stop_type
                    )

            if surplus_trips:
                # a trip has been removed from the route
                StopOrder.objects.filter(
                    trips_year=self.trips_year_id,
                    trip__in=surplus_trips, bus=self,
                    stop_type=stop_type
                ).delete()

        return self.stoporder_set.all()

    def order_stops(self):
        """
        Query StopOrder objects and order
        """
        return [o.stop for o in self.update_stop_ordering()]

    def over_capacity(self):
        """
        Returns True if the bus will be too full at
        some point on it's route.
        """
        stops = self.get_stops()
        load = 0
        for stop in stops:
            for trip in stop.trips_picked_up:
                load += trip.size()
            for trip in stop.trips_dropped_off:
                load -= trip.size()
            if load > self.route.vehicle.capacity:
                return True
        return False

    def directions(self):
        """
        Directions from Hanover to the Lodge, with information
        about where to dropoff and pick up each trip.

        TODO: refactor
        """
        stops = self.get_stops()
        load = 0
        for stop in stops:
            for trip in stop.trips_picked_up:
                load += trip.size()
            for trip in stop.trips_dropped_off:
                load -= trip.size()
            if load > self.route.vehicle.capacity:
                stop.over_capacity = True
            else:
                stop.over_capacity = False
            stop.passenger_count = load
        return get_directions(stops)

    def update_url(self):
        return reverse('db:scheduledtransport_update', kwargs=self.obj_kwargs())

    def detail_url(self):
        kwargs = {
            'trips_year': self.trips_year_id,
            'route_pk': self.route_id,
            'date': self.date
        }
        return reverse('db:scheduledtransport_checklist', kwargs=kwargs)

    def __str__(self):
        return "%s: %s" % (self.route, self.date.strftime("%x"))


class StopOrder(DatabaseModel):
    """
    Ordering of stops on an internal bus.

    The ordering field is called 'distance' to match the same
    field on the Stop model.

    This is basically the through model of an M2M relationship.
    """
    bus = models.ForeignKey(ScheduledTransport)
    order = models.PositiveSmallIntegerField()
    trip = models.ForeignKey('trips.Trip')
    PICKUP = 'PICKUP'
    DROPOFF = 'DROPOFF'
    stop_type = models.CharField(
        max_length=10, choices=(
            (PICKUP, PICKUP),
            (DROPOFF, DROPOFF),
        )
    )

    objects = StopOrderManager()

    class Meta:
        unique_together = ['trips_year', 'bus', 'trip']
        ordering = ['order']
        
    @property
    def stop(self):
        if self.stop_type == self.DROPOFF:
            return self.trip.template.dropoff_stop
        elif self.stop_type == self.PICKUP:
            return self.trip.template.pickup_stop
        raise Exception('bad stop_type %s' % self.stop_type)

    def save(self, **kwargs):
        """
        Automatically populate order from self.stop.distance
        """
        if self.order is None and self.stop:
            self.order = self.stop.distance
        return super(StopOrder, self).save(**kwargs)


class ExternalBus(DatabaseModel):
    """
    Bus used to transport local-section students to and
    from campus.
    """
    objects = ExternalBusManager()
    passengers = ExternalPassengerManager()
   
    route = models.ForeignKey(Route, on_delete=models.PROTECT)
    section = models.ForeignKey('trips.Section', on_delete=models.PROTECT)

    class Meta:
        unique_together = ('trips_year', 'route', 'section')
    
    def clean(self):
        if self.route.category == Route.INTERNAL:
            raise ValidationError("route must be external")

    @cache_as('_psngrs_to_hanover')
    def passengers_to_hanover(self):
        from doc.incoming.models import IncomingStudent
        return IncomingStudent.objects.passengers_to_hanover(
            self.trips_year_id, self.route, self.section
        )

    @cache_as('_psngrs_from_hanover')
    def passengers_from_hanover(self):
        from doc.incoming.models import IncomingStudent
        return IncomingStudent.objects.passengers_from_hanover(
            self.trips_year_id, self.route, self.section
        )

    DROPOFF_ATTR = 'dropoff'
    PICKUP_ATTR = 'pickup'
    def get_stops_to_hanover(self):
        """
        All stops the bus makes on it's way to Hanover.
       
        The passengers who are picked up and dropped off
        at each stop are stored in DROPOFF_ATTR and PICKUP_ATTR.
        """
        from doc.transport.constants import Hanover
        
        d = defaultdict(list)
        for p in self.passengers_to_hanover():
            d[p.get_bus_to_hanover()].append(p)
        for stop, psngrs in d.items():
            setattr(stop, self.DROPOFF_ATTR, [])
            setattr(stop, self.PICKUP_ATTR, psngrs)

        # TODO: sort passengers by last name

        hanover = Hanover()
        setattr(hanover, self.DROPOFF_ATTR, self.passengers_to_hanover())
        setattr(hanover, self.PICKUP_ATTR, [])

        return list(sorted(d.keys(), key=lambda x: x.distance)) + [hanover]

    def directions_to_hanover(self):
        stops = self.get_stops_to_hanover()
        load = 0
        for stop in stops:
            load -= len(getattr(stop, self.DROPOFF_ATTR))
            load += len(getattr(stop, self.PICKUP_ATTR))
            if load > self.route.vehicle.capacity:
                stop.over_capacity = True
            stop.passenger_count = load
        return get_directions(stops)

    def __str__(self):
        return "Section %s %s" % (self.section.name, self.route)
