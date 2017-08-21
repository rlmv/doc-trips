from django import forms

from fyt.transport.models import StopOrder
from fyt.utils.forms import ReadonlyFormsetMixin


class StopOrderFormset(ReadonlyFormsetMixin, forms.models.modelformset_factory(
        StopOrder, fields=['order', 'custom_time'], extra=0)):

    readonly_data = [
        ('Stop', 'get_stop'),
        ('Stop Type', 'get_stop_type'),
        ('Trip', 'get_trip'),
    ]

    def get_stop(self, instance):
        return instance.stop

    def get_stop_type(self, instance):
        return instance.stop_type

    def get_trip(self, instance):
        return instance.trip
