
import collections
from datetime import datetime, timedelta

from django.contrib import admin
from django.db.models import Q

from fyt.db.models import TripsYear
from fyt.trips.models import Campsite, TripType, TripTemplate, Trip, Section


class CampsiteAdmin(admin.ModelAdmin):

    list_display = ['name', 'dates']

    def get_camping_dates(self, trips_year):

        # -----------------
        # TODO: move this somewhere like the section object or manager
        # TODO: must support archival views - doesn't this? vv

        sections = Section.objects.filter(trips_year=trips_year)

        nights_camping = set()
        for section in sections:
            nights_camping.update(section.nights_camping)

        camping_dates = sorted(list(nights_camping))
        # -------------------------
        return camping_dates

    def dates(self, campsite):
        """ Display the number of people staying at a campsite
        (supposing all trips are maxed out) for all dates.

        TODO: remove this, or use some in a caching strategy for get_list_display
        """
        trips_year = campsite.trips_year
        camping_dates = self.get_camping_dates(trips_year)

        # TODO: set table header of dates, instead of literal 'dates' string

        # all trips which stay at campsite
        resident_trips = (Trip.objects
                          .filter(trips_year=trips_year)
                          .filter(Q(template__campsite_1=campsite) |
                                  Q(template__campsite_2=campsite)))

        # mapping of dates -> number of people staying at campsite on that date
        num_people_per_date = collections.defaultdict(int)

        for trip in resident_trips:
            if trip.template.campsite_1 == campsite:
                num_people_per_date[trip.section.at_campsite_1] += trip.template.max_num_people
            if trip.template.campsite_2 == campsite:
                num_people_per_date[trip.section.at_campsite_2] += trip.template.max_num_people

        return ' | '.join(map(lambda d: str(num_people_per_date.get(d, '-')), camping_dates))

    # return '|'.join(map(str, camping_dates))

    def get_list_display(self, request):

        """ Add all dates camping for the current section.

        Creates a table of campsite occupancies.
        """

        # WARNING
        # TODO: get this from request, not thin air
        trips_year = TripsYear.objects.current()
        camping_dates = self.get_camping_dates(trips_year)

        return self.list_display + list(map(str, camping_dates))

    def __getattr__(self, attr):
        """ Allow list_displayed camping dates to be accessed

        These dates return ____

        TODO: is there a more efficient way to do this? We're currently
        making m*n queries, one for each entry in the table. Can we cache
        anything?

        TODO: write test for this.
        """
        try:
            date = datetime.strptime(attr, '%Y-%m-%d').date()
        except ValueError:
            return super(CampsiteAdmin, self).__getattr__(self, attr)
        else:

            def date_capacity_getter(campsite):

                trips_year = campsite.trips_year

                # timedelta do the same thing as at_campsite_1/2 properties.
                # We want all trips which are staying at campsite on date.
                resident_trips = (
                    Trip.objects
                    .filter(trips_year=trips_year)
                    .filter(Q(template__campsite_1=campsite,
                              section__leaders_arrive=date-timedelta(days=2)) |
                            Q(template__campsite_2=campsite,
                              section__leaders_arrive=date-timedelta(days=3))))

                num_residents = 0
                for trip in resident_trips:

                    if (date == trip.section.at_campsite_1 and
                            campsite == trip.template.campsite_1):
                        num_residents += trip.template.max_num_people

                    if (date == trip.section.at_campsite_2 and
                            campsite == trip.template.campsite_2):
                        num_residents += trip.template.max_num_people

                return num_residents

            date_capacity_getter.short_description = date.strftime('%m-%d')

            return date_capacity_getter


class TripTypeAdmin(admin.ModelAdmin):

    """ Admin page for trip types.

    Interface is minimal, should not need any actions besides editing.
    """

    list_display = ['name', 'leader_description', 'trippee_description', 'packing_list']
    list_display_links = list_display
    actions = None


class TripTemplateAdmin(admin.ModelAdmin):

    list_display = ['name', 'description_summary', 'triptype']


admin.site.register(Campsite, CampsiteAdmin)
admin.site.register(TripType, TripTypeAdmin)
admin.site.register(TripTemplate, TripTemplateAdmin)
admin.site.register(Trip)
admin.site.register(Section)
