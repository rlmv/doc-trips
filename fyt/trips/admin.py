from django.contrib import admin

from fyt.trips.models import Campsite, Section, Trip, TripTemplate, TripType


admin.site.register(Campsite)
admin.site.register(TripType)
admin.site.register(TripTemplate)
admin.site.register(Trip)
admin.site.register(Section)
