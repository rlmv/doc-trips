
import collections

from django.contrib import admin
from django.db.models import Q

from db.models import TripsYear
from trip.models import Campsite, TripType, TripTemplate, ScheduledTrip, Section

class CampsiteAdmin(admin.ModelAdmin):

    list_display = ['name', 'dates']

    def dates(self, campsite): 
        """ Display the number of people staying at a campsite 
        (supposing all trips are maxed out) for all dates.
        """
        
        # TODO: set table header of dates, instead of literal 'dates' string

        # -----------------
        # TODO: move this somewhere like the section object or manager
        # TODO: must support archival views - doesn't this? vv
        trips_year = campsite.trips_year

        sections = Section.objects.filter(trips_year=trips_year)

        nights_camping = set() 
        for section in sections:
            nights_camping.update(section.nights_camping)
        
        camping_dates = sorted(list(nights_camping))
        # -------------------------

        # all trips which stay at campsite
        resident_trips = (ScheduledTrip.objects
            .filter(trips_year=trips_year)
            .filter(Q(template__campsite_1=campsite) | Q(template__campsite_2=campsite)))

        # mapping of dates -> number of people staying at campsite on that date
        num_people_per_date = collections.defaultdict(int)

        for trip in resident_trips:
            if trip.template.campsite_1 == campsite:
                num_people_per_date[trip.section.at_campsite_1] += trip.template.max_num_people
            if trip.template.campsite_2 == campsite:
                num_people_per_date[trip.section.at_campsite_2] += trip.template.max_num_people
        
        return ' | '.join(map(lambda d: str(num_people_per_date.get(d, '-')), camping_dates))

        # return '|'.join(map(str, camping_dates))


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
