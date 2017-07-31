from django.db.models.signals import post_save
from django.dispatch import receiver

from fyt.transport.models import InternalBus, StopOrder
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


@receiver(post_save, sender=Trip)
def update_ordering_for_trip_changes(instance, created, **kwargs):
    """
    Stop orderings need to be updated when a Trip is created or the dropoff
    and return routes of the Trip are changed.
    """
    if created or instance.tracker.has_changed('dropoff_route'):
        # Delete existing orderings (does nothing when created)
        instance.stoporder_set.filter(stop_type=StopOrder.DROPOFF).delete()

        new_bus = instance.get_dropoff_bus()
        if new_bus:
            create_dropoff(new_bus, instance)

    if created or instance.tracker.has_changed('pickup_route'):
        # Delete existing (NoOp when created)
        instance.stoporder_set.filter(stop_type=StopOrder.PICKUP).delete()

        new_bus = instance.get_pickup_bus()
        if new_bus:
            create_pickup(new_bus, instance)


# @receiver(post_save, sender=TripTemplate)
# def update_ordering_for_changed_triptemplate_stops(instance, **kwargs):

#     # TODO: for efficiency, check if the stop actually changed:
#     # if template.dropoff_stop.changed() or template.pickup_stop.changed():
#     affected_buses = InternalBus.objects.filter(
#         stoporder__trip__template=instance)

#     for bus in affected_buses:
#         bus.update_stop_ordering()
