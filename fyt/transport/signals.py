from django.db.models.signals import post_save
from django.dispatch import receiver

from fyt.transport.models import InternalBus, StopOrder, Stop
from fyt.trips.models import Trip, TripTemplate, Section


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


@receiver(post_save, sender=InternalBus)
def create_ordering_for_new_bus(instance, created, **kwargs):
    """
    Generate ordering for a new bus.
    """
    if created:
        for trip in instance.dropping_off():
            create_dropoff(instance, trip)

        for trip in instance.picking_up():
            create_pickup(instance, trip)


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


@receiver(post_save, sender=TripTemplate)
def update_ordering_for_triptemplate_stop_changes(instance, created, **kwargs):
    """
    Orderings are changed when the stops of a TripTemplate change.
    """
    if not created and instance.tracker.has_changed('dropoff_stop'):
        for trip in Trip.objects.filter(template=instance):
            resolve_dropoff(trip)

    if not created and instance.tracker.has_changed('pickup_stop'):
        for trip in Trip.objects.filter(template=instance):
            resolve_pickup(trip)


@receiver(post_save, sender=Section)
def update_ordering_for_section_date_change(instance, created, **kwargs):
    """
    Orderings are changed when the date of a Section changes.
    """
    if not created and instance.tracker.has_changed('leaders_arrive'):
        for trip in Trip.objects.filter(section=instance):
            resolve_dropoff(trip)
            resolve_pickup(trip)
