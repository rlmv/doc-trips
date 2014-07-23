
from django.contrib import admin

from trip.models import Campsite, TripType, TripTemplate, ScheduledTrip, Section

admin.site.register(Campsite)
admin.site.register(TripType)
admin.site.register(TripTemplate)
admin.site.register(ScheduledTrip)
admin.site.register(Section)
