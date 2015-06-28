from django.contrib import admin
from doc.transport.models import (
    Vehicle, Route, ScheduledTransport, ExternalBus
)

admin.site.register(Vehicle)
admin.site.register(Route)
admin.site.register(ScheduledTransport)
admin.site.register(ExternalBus)
