from django.db.models.signals import post_save
from django.dispatch import receiver

from fyt.transport.models import InternalBus


@receiver(post_save, sender=InternalBus)
def update_ordering_for_bus(instance, **kwargs):
    instance.update_stop_ordering()
