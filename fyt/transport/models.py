from collections import defaultdict
from copy import copy
from datetime import datetime, timedelta
from itertools import takewhile

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.functional import cached_property
from model_utils import FieldTracker

from fyt.db.models import DatabaseModel
from fyt.incoming.models import IncomingStudent
from fyt.transport.category import INTERNAL, EXTERNAL
from fyt.transport.managers import (
    ExternalBusManager,
    ExternalPassengerManager,
    RouteManager,
    InternalBusManager,
    StopManager,
    StopOrderManager,
)
from fyt.transport.maps import get_directions
from fyt.trips.models import Trip
from fyt.utils.cache import cache_as
from fyt.utils.lat_lng import validate_lat_lng


def sort_by_distance(stops, reverse=False):
    """
    Given an iterable of stops, return a list
    sorted by the distance field.
    """
    return sorted(stops, key=lambda x: x.distance, reverse=reverse)


class TransportConfig(DatabaseModel):
    """
    Configuration for each trips year, specifying which stops to use for
    Hanover and the Lodge. This was added in 2017 because the new Lodge was not
    complete in time for Trips.
    """
    class Meta:
        unique_together = ['trips_year']

    hanover = models.ForeignKey(
        'Stop',
        related_name="+",
        on_delete=models.PROTECT,
        help_text='The address at which bus routes start and stop in Hanover.')

    lodge = models.ForeignKey(
        'Stop',
        related_name="+",
        on_delete=models.PROTECT,
        help_text='The address of the Lodge.')


def Hanover(trips_year):
    """
    Return the Hanover Stop for this year.
    """
    return TransportConfig.objects.get(trips_year=trips_year).hanover


def Lodge(trips_year):
    """
    Return the Lodge Stop for this year.
    """
    return TransportConfig.objects.get(trips_year=trips_year).lodge


class Stop(DatabaseModel):
    """
    A stop on a transportation route.

    Represents a pickup or dropoff point for a trip OR a
    bus stop where local sections are picked up.
    """

    class Meta:
        ordering = ['name']

    objects = StopManager()
    tracker = FieldTracker(fields=['route'])

    name = models.CharField(max_length=255)
    address = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text=(
            "Plain text address, eg. Hanover, NH 03755. This must "
            "take you to the location in Google maps."))

    lat_lng = models.CharField(
        'coordinates',
        max_length=255,
        blank=True,
        default='',
        validators=[validate_lat_lng],
        help_text="Latitude & longitude coordinates, eg. 43.7030,-72.2895")

    # verbal directions, descriptions. migrated from legacy.
    directions = models.TextField(blank=True)

    route = models.ForeignKey(
        'Route',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='stops',
        help_text="default bus route")

    # costs are required for EXTERNAL stops
    cost_round_trip = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="for external buses")

    cost_one_way = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="for external buses")

    # mostly used for external routes
    dropoff_time = models.TimeField(blank=True, null=True)
    pickup_time = models.TimeField(blank=True, null=True)

    distance = models.PositiveIntegerField(help_text=(
        "this rough distance from Hanover is used for bus routing"))

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
        if self.route is None:
            return None
        return self.route.category

    @property
    def location(self):
        """
        Get the location of the stop. Coordinates are
        probably more accurate so we return them if possible.
        """
        return self.lat_lng or self.address

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
    INTERNAL = INTERNAL
    EXTERNAL = EXTERNAL
    category = models.CharField(
        max_length=20,
        choices=(
            (INTERNAL, 'Internal'),
            (EXTERNAL, 'External')))

    vehicle = models.ForeignKey('Vehicle', on_delete=models.PROTECT)

    display_color = models.CharField(
        max_length=20,
        default="white",
        help_text="The color to use when displaying this route in tables.")

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


class InternalBus(DatabaseModel):
    """
    Represents a scheduled internal transport.
    """
    objects = InternalBusManager()

    route = models.ForeignKey(Route, on_delete=models.PROTECT)
    date = models.DateField()
    notes = models.TextField(help_text='for the bus driver')

    dirty = models.BooleanField(
        'Do directions and times need to be updated?',
        default=True, editable=False)

    class Meta:
        unique_together = ['trips_year', 'route', 'date']
        ordering = ['date']

    def clean(self):
        if self.route.category == Route.EXTERNAL:
            raise ValidationError("route must be internal")

    # TODO: move the main implementation of the trip methods to here?
    # We could just instantiate a transport object without saving and
    # call the methods on it.

    def dropping_off(self):
        """
        All trips which this transport drops off (on the trip's day 2)
        """
        return Trip.objects.dropoffs(
            self.route, self.date, self.trips_year_id
        ).select_related(
            'template__dropoff_stop')

    def picking_up(self):
        """
        All trips which this transport picks up (on trip's day 4)
        """
        return Trip.objects.pickups(
            self.route, self.date, self.trips_year_id
        ).select_related(
            'template__pickup_stop')

    def returning(self):
        """
        All trips which this transport returns to Hanover (on day 5)
        """
        return Trip.objects.returns(self.route, self.date, self.trips_year_id)

    @cached_property
    def trip_cache(self):
        """
        A cache of Trips with preloaded size attributes.
        """
        if not hasattr(self, '_trip_cache'):
            self.load_trip_cache(
                None,
                self.dropping_off(),
                self.picking_up(),
                self.returning(),
                Hanover(self.trips_year),
                Lodge(self.trips_year))

        return self._trip_cache

    class TripCache:
        """
        Cache for various preloaded bus properties.
        """
        def __init__(self, trips, dropoffs, pickups, returns, hanover, lodge):
            self.trip_dict = None if trips is None else {t: t for t in trips}
            self.dropoffs = dropoffs
            self.pickups = pickups
            self.returns = returns
            self._hanover = hanover
            self._lodge = lodge

        # Return copies so that each instance can have different pickup/dropoff
        # attributes

        @property
        def hanover(self):
            return copy(self._hanover)

        @property
        def lodge(self):
            return copy(self._lodge)

        def get(self, value):
            if self.trip_dict is None:
                return value
            return self.trip_dict[value]

    def load_trip_cache(self, all_trips, dropoffs, pickups, returns, hanover, lodge):
        """
        Load the trip cache.
        """
        self._trip_cache = InternalBus.TripCache(
            all_trips,
            dropoffs,
            pickups,
            returns,
            hanover,
            lodge)

    @cache_as('_get_stops')
    def get_stops(self):
        """
        All stops which the bus makes as it drops trips off
        and picks them up. The first stop is Hanover, the last
        is the Lodge. Intermediate stops are ordered by their
        distance from Hanover.

        Each stop has a trips_dropped_off and trips_picked_up
        property added to it which contain the list of trips which are dropped
        off and picked up at this stop by this bus.
        """
        DROPOFF_ATTR = 'trips_dropped_off'
        PICKUP_ATTR = 'trips_picked_up'

        def set_trip_attr(stop, order):
            for attr in [DROPOFF_ATTR, PICKUP_ATTR]:
                if not hasattr(stop, attr):
                    setattr(stop, attr, [])

            if order.stop_type == StopOrder.DROPOFF:
                getattr(stop, DROPOFF_ATTR).append(self.trip_cache.get(order.trip))

            if order.stop_type == StopOrder.PICKUP:
                getattr(stop, PICKUP_ATTR).append(self.trip_cache.get(order.trip))

            return stop

        picking_up = self.trip_cache.pickups
        dropping_off = self.trip_cache.dropoffs
        returning = self.trip_cache.returns

        stops = []
        for order in self.stoporder_set.all():
            if len(stops) == 0 or stops[-1] != order.stop:  # new stop
                stops.append(set_trip_attr(order.stop, order))
            else:  # another trip for the same stop
                set_trip_attr(stops[-1], order)

        # all buses start from Hanover
        hanover = self.trip_cache.hanover
        setattr(hanover, PICKUP_ATTR, list(dropping_off))
        setattr(hanover, DROPOFF_ATTR, [])
        stops = [hanover] + stops

        if self.visits_lodge:
            # otherwise we can bypass the lodge
            lodge = self.trip_cache.lodge
            setattr(lodge, DROPOFF_ATTR, list(picking_up))
            setattr(lodge, PICKUP_ATTR, list(returning))
            stops.append(lodge)

        if returning:
            # Take trips back to Hanover.
            # Load attributes onto a fresh Stop object.
            hanover = self.trip_cache.hanover
            setattr(hanover, DROPOFF_ATTR, list(returning))
            setattr(hanover, PICKUP_ATTR, [])
            stops.append(hanover)

        return stops

    @property
    def visits_lodge(self):
        return self.trip_cache.pickups or self.trip_cache.returns

    def update_stop_times(self):
        """
        Go through the bus route and update the times at which trips are
        picked up and dropped off.
        """
        directions = self.directions()

        # Time it takes to load and unload trips
        LOADING_TIME = timedelta(minutes=15)

        # Leave at 7:30 AM
        DEPARTURE_TIME = datetime(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=7,
            minute=30)

        # Don't get to the Lodge before 11
        MIN_LODGE_ARRIVAL_TIME = datetime(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=11)

        legs_to_lodge = list(
            takewhile(lambda leg: leg.start_stop != self.trip_cache.lodge,
                      directions.legs))

        travel_time = sum((leg.duration for leg in legs_to_lodge), timedelta())
        loading_time = (len(legs_to_lodge) - 1) * LOADING_TIME
        total_duration = travel_time + loading_time

        # Don't arrive at the Lodge until 11am
        if (self.visits_lodge and (
                DEPARTURE_TIME + total_duration < MIN_LODGE_ARRIVAL_TIME)):
            progress = MIN_LODGE_ARRIVAL_TIME - total_duration
        else:
            progress = DEPARTURE_TIME

        # TODO: wrap this whole update in a transaction?
        for leg in legs_to_lodge:

            if leg.start_stop != self.trip_cache.hanover:
                for trip in leg.start_stop.trips_picked_up:
                    stoporder = trip.get_pickup_stoporder()
                    stoporder.computed_time = progress.time()
                    stoporder.save()

                progress += LOADING_TIME

            leg.start_time = progress.time()
            progress += leg.duration
            leg.end_time = progress.time()

            if leg.end_stop != self.trip_cache.lodge:
                for trip in leg.end_stop.trips_dropped_off:
                    stoporder = trip.get_dropoff_stoporder()
                    stoporder.computed_time = progress.time()
                    stoporder.save()

        self.dirty = False
        self.save()

        return directions

    def validate_stop_ordering(self):
        """
        Sanity check the stop orderings for this bus are correct.
        """
        def stoporders_by_type(type):
            return filter(lambda x: x.stop_type == type, self.stoporder_set.all())

        opts = (
            (StopOrder.PICKUP, self.picking_up(),
             lambda x: x.template.pickup_stop),
            (StopOrder.DROPOFF, self.dropping_off(),
             lambda x: x.template.dropoff_stop)
        )

        for stop_type, trips, stop_getter in opts:
            ordered_trips = set([x.trip for x in stoporders_by_type(stop_type)])
            unordered_trips = set(trips) - ordered_trips
            surplus_trips = ordered_trips - set(trips)

            if unordered_trips:
                raise ValidationError(
                    f'Unordered {stop_type} trips for bus {self}: '
                    f'{unordered_trips}')

            if surplus_trips:
                # a trip has been removed from the route
                raise ValidationError(
                    f'Surplus {stop_type} trips for bus {self}: '
                    f'{surplus_trips}')

    def get_stop_ordering(self):
        """
        Get the StopOrder objects for this bus.

        For now, this returns a fresh QuerySet in case the orderings are
        prefetched.

        TODO: use `stoporder_set.all()`
        """
        return StopOrder.objects.filter(bus=self)

    def over_capacity(self):
        """
        Returns True if the bus will be too full at
        some point on its route.
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

    def detail_url(self):
        kwargs = {
            'trips_year': self.trips_year_id,
            'route_pk': self.route_id,
            'date': self.date
        }
        return reverse('db:internalbus:checklist', kwargs=kwargs)

    def __str__(self):
        return "%s: %s" % (self.route, self.date.strftime("%x"))


class StopOrder(DatabaseModel):
    """
    Ordering of stops on an internal bus.

    One such object exists for each stop that the bus makes to dropoff
    and pickup trips in between Hanover and the Lodge.

    StopOrderings are affected by many other objects. These changes are
    managed by signals in `fyt.transport.signals.

    This is essentially the through model of an M2M relationship.
    """
    bus = models.ForeignKey(InternalBus, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)

    computed_time = models.TimeField(
        'Pickup/dropoff time computed by Google Maps',
        null=True, default=None, editable=False)

    PICKUP = 'PICKUP'
    DROPOFF = 'DROPOFF'
    stop_type = models.CharField(
        max_length=10,
        choices=(
            (PICKUP, PICKUP),
            (DROPOFF, DROPOFF)))

    objects = StopOrderManager()

    class Meta:
        unique_together = ['trips_year', 'bus', 'trip']
        ordering = ['order']

    # TODO: handle time calculations more efficiently
    @property
    def time(self):
        """
        Re-compute pickup and dropoff times for this bus.
        """
        self.bus.update_stop_times()
        self.refresh_from_db()
        return self.computed_time

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
        return super().save(**kwargs)

    def __str__(self):
        return f'{self.stop_type}: {self.trip} {self.bus.date}'


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

    @property
    def date_to_hanover(self):
        """
        Date bus takes trippees to Hanover
        """
        return self.section.trippees_arrive

    @property
    def date_from_hanover(self):
        """
        Date bus takes trippees home after trips
        """
        return self.section.return_to_campus

    @cache_as('_psngrs_to_hanover')
    def passengers_to_hanover(self):
        return IncomingStudent.objects.passengers_to_hanover(
            self.trips_year_id, self.route, self.section)

    @cache_as('_psngrs_from_hanover')
    def passengers_from_hanover(self):
        return IncomingStudent.objects.passengers_from_hanover(
            self.trips_year_id, self.route, self.section)

    def all_passengers(self):
        def pks(qs):
            return [x.pk for x in qs]
        return IncomingStudent.objects.filter(pk__in=(
            pks(self.passengers_to_hanover()) +
            pks(self.passengers_from_hanover()))
        ).order_by('name')

    DROPOFF_ATTR = 'dropoff'
    PICKUP_ATTR = 'pickup'

    def get_stops_to_hanover(self):
        """
        All stops the bus makes on it's way to Hanover.

        The passengers who are picked up and dropped off
        at each stop are stored in DROPOFF_ATTR and PICKUP_ATTR.
        """
        d = defaultdict(list)
        for p in self.passengers_to_hanover():
            d[p.get_bus_to_hanover()].append(p)
        for stop, psngrs in d.items():
            setattr(stop, self.DROPOFF_ATTR, [])
            setattr(stop, self.PICKUP_ATTR, psngrs)

        hanover = Hanover(self.trips_year)
        setattr(hanover, self.DROPOFF_ATTR, self.passengers_to_hanover())
        setattr(hanover, self.PICKUP_ATTR, [])

        return sort_by_distance(d.keys(), reverse=True) + [hanover]

    def get_stops_from_hanover(self):
        """
        All stops the bus makes as it drop trippees off after trips.
        """
        d = defaultdict(list)
        for p in self.passengers_from_hanover():
            d[p.get_bus_from_hanover()].append(p)
        for stop, psngrs in d.items():
            setattr(stop, self.DROPOFF_ATTR, psngrs)
            setattr(stop, self.PICKUP_ATTR, [])

        hanover = Hanover(self.trips_year)
        setattr(hanover, self.DROPOFF_ATTR, [])
        setattr(hanover, self.PICKUP_ATTR, self.passengers_from_hanover())

        return [hanover] + sort_by_distance(d.keys())

    def directions_to_hanover(self):
        return self._directions(self.get_stops_to_hanover())

    def directions_from_hanover(self):
        return self._directions(self.get_stops_from_hanover())

    def _directions(self, stops):
        """
        Compute capacity and passenger count, then return
        Google Maps directions.
        """
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
