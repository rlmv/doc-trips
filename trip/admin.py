
from django.contrib import admin

from trip.models import Campsite, TripType, TripTemplate, ScheduledTrip, Section

class CampsiteAdmin(admin.ModelAdmin):

    pass

admin.site.register(Campsite, CampsiteAdmin)
admin.site.register(TripType)
admin.site.register(TripTemplate)
admin.site.register(ScheduledTrip)
admin.site.register(Section)
