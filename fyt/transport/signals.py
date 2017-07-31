from django.db.models.signals import post_save
from django.dispatch import receiver

from fyt.transport.models import InternalBus, StopOrder, Stop
from fyt.trips.models import Trip, TripTemplate


@receiver(post_save, sender=InternalBus)
def update_ordering_for_bus(instance, **kwargs):
    instance.update_stop_ordering()


def create_dropoff(bus, trip):
    return StopOrder.objects.create(
        trips_year=bus.trips_year,
        bus=bus,
        trip=trip,
        stop_type=StopOrder.DROPOFF)


def create_pickup(bus, trip):
    return StopOrder.objects.create(
        trips_year=bus.trips_year,
        bus=bus,
        trip=trip,
        stop_type=StopOrder.PICKUP)


def resolve_dropoff(trip):
    # Delete existing orderings (does nothing when created)
    trip.stoporder_set.filter(stop_type=StopOrder.DROPOFF).delete()

    new_bus = trip.get_dropoff_bus()
    if new_bus:
        create_dropoff(new_bus, trip)


def resolve_pickup(trip):
    # Delete existing (NoOp when created)
    trip.stoporder_set.filter(stop_type=StopOrder.PICKUP).delete()

    new_bus = trip.get_pickup_bus()
    if new_bus:
        create_pickup(new_bus, trip)


@receiver(post_save, sender=Trip)
def update_ordering_for_trip_changes(instance, created, **kwargs):
    """
    Stop orderings need to be updated when a Trip is created or the dropoff
    and return routes of the Trip are changed.
    """
    if created or instance.tracker.has_changed('dropoff_route'):
        resolve_dropoff(instance)

    if created or instance.tracker.has_changed('pickup_route'):
        resolve_pickup(instance)


# TODO: move Trip.route overrides to the StopOrder itself?
@receiver(post_save, sender=Stop)
def update_ordering_for_stop_changes(instance, created, **kwargs):
    """
    Orderings are updated when a Stop changes its route.

    Only Trips that do not have dropoffs or pickups overridden on the Trip
    itself are affected.
    """
    if not created and instance.tracker.has_changed('route'):

        # TODO: move these to manager methods?
        affected_dropoffs = Trip.objects.filter(
            template__dropoff_stop=instance,
            dropoff_route=None)

        affected_pickups = Trip.objects.filter(
            template__pickup_stop=instance,
            pickup_route=None)

        for trip in affected_dropoffs:
            resolve_dropoff(trip)

        for trip in affected_pickups:
            resolve_pickup(trip)


# @receiver(post_save, sender=TripTemplate)
# def update_ordering_for_changed_triptemplate_stops(instance, **kwargs):

#     # TODO: for efficiency, check if the stop actually changed:
#     # if template.dropoff_stop.changed() or template.pickup_stop.changed():
#     affected_buses = InternalBus.objects.filter(
#         stoporder__trip__template=instance)

#     for bus in affected_buses:
#         bus.update_stop_ordering()
