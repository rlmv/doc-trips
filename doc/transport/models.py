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
        on_delete=models.PROTECT, related_name='stops'
    )
    # TODO: validate that this only is used if route.category==EXTERNAL?
    cost = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    # mostly used for external routes
    pickup_time = models.TimeField(blank=True, null=True)
    dropoff_time = models.TimeField(blank=True, null=True)
    distance = models.IntegerField(help_text=(
        "this rough distance from Hanover is used for bus routing"
    ))

    def clean(self):
        if not self.lat_lng and not self.address:
            raise ValidationError(
                "%s must set either lat_lng or address" % self)

    @property
    def category(self):
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

    def get_detail_url(self):
        return reverse('db:stop_detail', kwargs=self.obj_kwargs())

    def __str__(self):
        return self.name

    def location_str(self):
        return "%s (%s)" % (self.name, self.location)


class Route(DatabaseModel):
    """
    A transportation route.

    A route is either INTERNAL (transporting students to/from Hanover,
    trip dropoffs/pickups, and the lodge) or EXTERNAl (moving local
    students to and from campus before and after their trips.)
    """
    name = models.CharField(max_length=255)
    INTERNAL = 'INTERNAL'
    EXTERNAL = 'EXTERNAL'
    TRANSPORT_CATEGORIES = (
        (INTERNAL, 'Internal'),
        (EXTERNAL, 'External'),
    )
    category = models.CharField(max_length=20, choices=TRANSPORT_CATEGORIES)
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

    class Meta:
        unique_together = ('trips_year', 'route', 'date')

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
            .select_related('template__dropoff')
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
            .select_related('template__pickup')
        )

    @cache_as('_returning')
    def returning(self):
        """
        All trips which this transport returns to Hanover (on day 5)
        """
        from doc.trips.models import Trip
        return Trip.objects.returns(self.route, self.date,
                                    self.trips_year_id)

    def all_stops(self):
        return set(
            list(map(lambda x: x.template.pickup, self.picking_up())) +
            list(map(lambda x: x.template.dropoff, self.dropping_off()))
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

        dropoff_dict = defaultdict(list)
        for trip in self.dropping_off():
            dropoff_dict[trip.template.dropoff] += [trip]

        pickup_dict = defaultdict(list)
        for trip in self.picking_up():
            pickup_dict[trip.template.pickup] += [trip]

        stops = self._order_stops()
        for stop in stops:
            stop.trips_dropped_off = dropoff_dict[stop]
            stop.trips_picked_up = pickup_dict[stop]

        # all buses go from Hanover to the Lodge
        hanover = Hanover()
        hanover.trips_picked_up = list(self.dropping_off())
        hanover.trips_dropped_off = []
        lodge = Lodge()
        lodge.trips_dropped_off = list(self.picking_up())
        lodge.trips_picked_up = []

        return [hanover] + list(stops) + [lodge]

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
        stops = self.all_stops()
        ordered_stops = set([x.stop for x in self._get_stoporder_set()])
        unordered_stops = set(stops) - ordered_stops
        surplus_stops = ordered_stops - set(stops)

        if unordered_stops:
            # we are missing some ordering objects
            for stop in unordered_stops:
                StopOrder.objects.create(
                    distance=stop.distance, stop=stop,
                    bus=self, trips_year_id=self.trips_year_id
                )

        elif surplus_stops:
            # a stop has been removed from the route
            StopOrder.objects.filter(
                trips_year=self.trips_year_id,
                stop__in=surplus_stops, bus=self
            ).delete()

        return self._get_stoporder_set()

    def _get_stoporder_set(self):
        return (
            self.stoporder_set.all()
            .order_by('distance')
            .select_related('stop')
        )

    def _order_stops(self):
        """
        Query StopOrder objects and order
        """
        return list(map(lambda x: x.stop, self.update_stop_ordering()))

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

    def __str__(self):
        return "%s: %s" % (self.route, self.date.strftime("%x"))


class StopOrder(DatabaseModel):
    """
    Ordering of stops on an internal bus.

    We are using a separate model instead of a comma 
    separated list on the internal bus since we want 
    to remember the relative distances of the stops so 
    we can integrate stops into the order as they are 
    added to a route.

    This is just a M2M relationship with a through field.
    """
    bus = models.ForeignKey(ScheduledTransport)
    stop = models.ForeignKey(Stop)
    distance = models.PositiveSmallIntegerField(blank=True)

    class Meta:
        unique_together = ('trips_year', 'bus', 'stop')

    objects = StopOrderManager

    def save(self, **kwargs):
        if self.distance is None and self.stop:
            self.distance = self.stop.distance
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

    def __str__(self):
        return "Section %s %s" % (self.section.name, self.route)
