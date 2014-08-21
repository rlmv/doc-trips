
from django.contrib import admin

from trip.models import Campsite, TripType, TripTemplate, ScheduledTrip, Section

class CampsiteAdmin(admin.ModelAdmin):

    pass


class TripTypeAdmin(admin.ModelAdmin):

    """ Admin page for trip types.

    Interface is minimal, should not need any actions besides editing.
    """

    list_display = ['name', 'leader_description', 'trippee_description', 'packing_list']
    list_display_links = list_display
    actions = None


class TripTemplateAdmin(admin.ModelAdmin):
    
    list_display = ['name', 'description', 'trip_type']


admin.site.register(Campsite, CampsiteAdmin)
admin.site.register(TripType, TripTypeAdmin)
admin.site.register(TripTemplate, TripTemplateAdmin)
admin.site.register(ScheduledTrip)
admin.site.register(Section)
