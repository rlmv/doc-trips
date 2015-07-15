from collections import defaultdict

from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from doc.db.models import DatabaseModel
from doc.transport.managers import (
    StopManager, RouteManager, ScheduledTransportManager,
    ExternalBusManager, ExternalPassengerManager
)
from doc.transport.maps import get_directions


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
    # TODO: validate that lat and long are interdependet / location is there?
    address = models.CharField(
        max_length=255, help_text=(
            "Plain text address, eg. Hanover, NH 03755. This must "
            "take you to the location in Google maps."
        )
    )
    lat_lng = models.CharField(max_length=255, blank=True, default='')
    
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
    distance = models.IntegerField(null=True)

    @property
    def category(self):
        return self.route.category

    def get_detail_url(self):
        return reverse('db:stop_detail', kwargs=self.obj_kwargs())

    def __str__(self):
        return self.name


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

    def dropping_off(self):
        """
        All trips which this transport drops off (on the trip's day 2)
        """
        from doc.trips.models import ScheduledTrip
        return ScheduledTrip.objects.dropoffs(self.route, self.date,
                                              self.trips_year)

    def picking_up(self):
        """
        All trips which this transport picks up (on trip's day 4)
        """
        from doc.trips.models import ScheduledTrip
        return ScheduledTrip.objects.pickups(self.route, self.date,
                                             self.trips_year)

    def returning(self):
        """
        All trips which this transport returns to Hanover (on day 5)
        """
        from doc.trips.models import ScheduledTrip
        return ScheduledTrip.objects.returns(self.route, self.date,
                                             self.trips_year)

    def dropoff_and_pickup_stops(self):
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
            
        stops = set(list(pickup_dict.keys()) + list(dropoff_dict.keys()))
        for stop in stops:
            stop.trips_dropped_off = dropoff_dict[stop]
            stop.trips_picked_up = pickup_dict[stop]

        # all buses go from Hanover to the Lodge
        hanover = Hanover()
        hanover.trips_picked_up = list(self.dropping_off())
        lodge = Lodge()
        lodge.trips_dropped_off = list(self.picking_up())

        stops = sorted(stops, key=lambda x: x.distance)
        return [hanover] + list(stops) + [lodge]

    def directions(self):
        """
        Directions from Hanover to the Lodge, with information
        about where to dropoff and pick up each trip.
        """
        return get_directions(self.dropoff_and_pickup_stops())

    def __str__(self):
        return "%s: %s" % (self.route, self.date.strftime("%x"))


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
