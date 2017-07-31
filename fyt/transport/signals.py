from django.db.models.signals import post_save
from django.dispatch import receiver

from fyt.transport.models import InternalBus
from fyt.trips.models import Trip


@receiver(post_save, sender=InternalBus)
def update_ordering_for_bus(instance, **kwargs):
    instance.update_stop_ordering()


@receiver(post_save, sender=Trip)
def add_new_trip_to_ordering(instance, created, **kwargs):
    if created:
        try:
            InternalBus.objects.get(
                route=instance.get_dropoff_route(),
                date=instance.dropoff_date
            ).update_stop_ordering()
        except InternalBus.DoesNotExist:
            pass

        try:
            InternalBus.objects.get(
                route=instance.get_pickup_route(),
                date=instance.pickup_date
            ).update_stop_ordering()
        except InternalBus.DoesNotExist:
            pass
