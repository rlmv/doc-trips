from django.contrib import admin

from fyt.transport.models import (
    ExternalBus,
    Route,
    ScheduledTransport,
    StopOrder,
    Vehicle,
)


admin.site.register(Vehicle)
admin.site.register(Route)
admin.site.register(ScheduledTransport)
admin.site.register(ExternalBus)
admin.site.register(StopOrder)
