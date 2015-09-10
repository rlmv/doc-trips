from django.contrib import admin
from fyt.transport.models import (
    Vehicle, Route, ScheduledTransport, ExternalBus, StopOrder
)

admin.site.register(Vehicle)
admin.site.register(Route)
admin.site.register(ScheduledTransport)
admin.site.register(ExternalBus)
admin.site.register(StopOrder)
