from django.contrib import admin

from fyt.transport.models import (
    ExternalBus,
    Route,
    InternalBus,
    StopOrder,
    Vehicle,
)


admin.site.register(Vehicle)
admin.site.register(Route)
admin.site.register(InternalBus)
admin.site.register(ExternalBus)
admin.site.register(StopOrder)
