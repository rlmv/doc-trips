import collections

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse

from db.models import DatabaseModel
from transport.models import Stop, Route
from trips.managers import SectionDatesManager


class ScheduledTrip(DatabaseModel):

    template = models.ForeignKey('TripTemplate', on_delete=models.PROTECT)
    section = models.ForeignKey('Section', on_delete=models.PROTECT)

    # The leaders for this trip can be accessed through the 'leaders' field.
    # See LeaderApplication.assigned_trip.

    class Meta:
        # no two ScheduledTrips can have the same template-section-trips_year
        # combination; we don't want to schedule two identical trips
        unique_together = ('template', 'section', 'trips_year')

    def __str__(self):

        # return '{}{}- {}'.format(self.section.name, self.template.name, self.template.description)
        return '{}{}'.format(self.section.name, self.template.name)

class Section(DatabaseModel):
    
    """ Model to represent a trips section. """

    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=1, help_text="A, B, C, etc.", verbose_name='Section') 
    leaders_arrive = models.DateField()
    
    is_local = models.BooleanField(default=False)
    is_exchange = models.BooleanField(default=False)
    is_transfer = models.BooleanField(default=False)
    is_international = models.BooleanField(default=False)
    is_fysep = models.BooleanField(default=False)
    is_native = models.BooleanField(default=False)
    
    objects = models.Manager()
    dates = SectionDatesManager()

    @property
    def trippees_arrive(self):
        """ Date that trippees arrive in Hanover. """
        return self.leaders_arrive + timedelta(days=1)

    @property
    def at_campsite1(self):
        return self.leaders_arrive + timedelta(days=2)

    @property
    def at_campsite2(self):
        return self.leaders_arrive + timedelta(days=3)

    @property
    def nights_camping(self):
        """ List of dates when trippees are camping out on the trail. """
        return [self.at_campsite1, self.at_campsite2]

    @property
    def arrive_at_lodge(self):
        """ Date section arrives at the lodge. """
        return self.leaders_arrive + timedelta(days=4)

    @property
    def return_to_campus(self):
        """ Date section returns to campus. """
        return self.leaders_arrive + timedelta(days=5)

    def __str__(self):
        return self.name
        
        
    def date_range_str(self):
        
        fmt = '%b %d'
        return (self.leaders_arrive.strftime(fmt) + ' to ' + 
                self.return_to_campus.strftime(fmt))
        

class TripTemplate(DatabaseModel):

    name = models.PositiveSmallIntegerField() # TODO: validate this to range [0-999]
    description_summary = models.CharField(max_length=255, verbose_name='Summary') # short info

    triptype = models.ForeignKey('TripType', verbose_name='trip type', on_delete=models.PROTECT)
    max_trippees = models.PositiveSmallIntegerField()
    non_swimmers_allowed = models.BooleanField(default=True)
    
    dropoff = models.ForeignKey(Stop, related_name='dropped_off_trips', on_delete=models.PROTECT)
    pickup = models.ForeignKey(Stop, related_name='picked_up_trips', on_delete=models.PROTECT)
    # is this for returning from the lodge?
    # TODO: remove null=True. All templates need a return route.
    return_route = models.ForeignKey(Route, related_name='returning_trips', null=True, on_delete=models.PROTECT)

    # TODO: better related names
    campsite1 = models.ForeignKey('Campsite', related_name='trip_night_1', on_delete=models.PROTECT)
    campsite2 = models.ForeignKey('Campsite', related_name='trip_night_2', on_delete=models.PROTECT)

    description_introduction = models.TextField(verbose_name='Introduction', blank=True)
    description_day1 = models.TextField(verbose_name='Day 1', blank=True)
    description_day2 = models.TextField(verbose_name='Day 2', blank=True)
    description_day3 = models.TextField(verbose_name='Day 3', blank=True)
    description_conclusion = models.TextField(verbose_name='Conclusion', blank=True)
    
    revision_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'template'
        ordering = ['name']

    @property
    def max_num_people(self):
        """ Maximum number of people on trip: max_trippees + 2 leaders """
        return self.max_trippees + 2

    def get_scheduled_trips(self):
        """ Get all scheduled trips which use this template 

        Returns a dictionary of section:scheduledtrip/None

        TODO: optimize this. Calling this for every row means a lot
        of redundant queries. 

        Can we compute the entire table with a constant number of queries? 
        """
        scheduled_trips = (ScheduledTrip.objects
                 .filter(trips_year=self.trips_year)
                 .filter(template=self))
        
        sections = Section.objects.filter(trips_year=self.trips_year)
        
        trips_by_section = {section: None for section in sections}
        
        for trip in scheduled_trips:
            trips_by_section[trip.section] = trip

        return trips_by_section

    def get_scheduled_trips_list(self):
        
        trips_by_section = self.get_scheduled_trips()
        keys = sorted(trips_by_section.keys(), key=(lambda s: s.name))
        return map(lambda k: trips_by_section[k], keys)

    def __str__(self):
        return "{}: {}".format(self.name, self.description_summary)


class TripType(DatabaseModel):
    
    name = models.CharField(max_length=255)
    leader_description = models.TextField()
    trippee_description = models.TextField()
    packing_list = models.TextField(blank=True) 
    # TODO: the packing list should be inherited, somehow.
    # can we have some sort of common/base packing list? and add in extras?

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Campsite(DatabaseModel):
    
    name = models.CharField(max_length=255)
    capacity = models.PositiveSmallIntegerField(null=True)
    directions = models.TextField()
    bugout = models.TextField() # directions for quick help/escape
    secret = models.TextField() # door codes, hidden things, other secret information

    def get_occupancy(self):
        """ Get all ScheduledTrips staying at this campsite
        
        Returns a dictionary of date:list(trips) pairs. 
        """
        
        trips_year = self.trips_year
        camping_dates = Section.dates.camping_dates(trips_year)

        # all trips which stay at campsite
        resident_trips = (ScheduledTrip.objects
                          .filter(trips_year=trips_year)
                          .filter(Q(template__campsite1=self) |
                                  Q(template__campsite2=self)))

        # mapping of dates -> trips at this campsite
        trips_by_date = {date: [] for date in camping_dates}

        for trip in resident_trips:
            if trip.template.campsite1 == self:
                trips_by_date[trip.section.at_campsite1].append(trip)
            if trip.template.campsite2 == self:
                trips_by_date[trip.section.at_campsite2].append(trip)

        return trips_by_date

    def get_occupancy_list(self):
        """ List of ScheduledTrips at campsite

        The occupancy has a one-to-one correspondance with Section.dates.camping_dates
        """
        
        occupancy = self.get_occupancy()
        keys = sorted(occupancy.keys())
        return map(lambda k: occupancy[k], keys)
    
    def __str__(self):
        return self.name
