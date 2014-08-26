

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse

from db.models import DatabaseModel


class ScheduledTrip(DatabaseModel):

    template = models.ForeignKey('TripTemplate')
    section = models.ForeignKey('Section')

    # The leaders for this trip can be accessed through the 'leaders' field.
    # See LeaderApplication.assigned_trip.

    absolute_url_pattern = 'db:trip:trip_update'
            
    def __str__(self):

        return '{}{} - {}'.format(self.section.name, self.template.name, self.template.description)


class Section(DatabaseModel):
    
    """ Model to represent a trips section. """

    name = models.CharField(max_length=1) # A,B,C, etc
    leaders_arrive = models.DateField()
    
    is_local = models.BooleanField(default=False)
    is_exchange = models.BooleanField(default=False)
    is_transfer = models.BooleanField(default=False)
    is_international = models.BooleanField(default=False)
    is_fysep = models.BooleanField(default=False)
    is_native = models.BooleanField(default=False)

    @property
    def trippees_arrive(self):
        """ Date that trippees arrive in Hanover. """
        return self.leaders_arrive + timedelta(days=1)

    @property
    def at_campsite_1(self):
        return self.leaders_arrive + timedelta(days=2)

    @property
    def at_campsite_2(self):
        return self.leaders_arrive + timedelta(days=3)

    @property
    def nights_camping(self):
        """ List of dates when trippees are camping out on the trail. """
        
        return [self.at_campsite_1, self.at_campsite_2]

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


class TripTemplate(DatabaseModel):

    name = models.PositiveSmallIntegerField() # TODO: validate this to range [0-999]
    description = models.CharField(max_length=255) # short info

    trip_type = models.ForeignKey('TripType')
    max_trippees = models.PositiveSmallIntegerField()
    non_swimmers_allowed = models.BooleanField(default=True)
    
    """ TODO:
    dropoff_transport_stop = models.ForeignKey('TransportStop')
    pickup_transport_stop = models.ForeignKey('TransportStop')
    """

    # TODO: better related names
    campsite_1 = models.ForeignKey('Campsite', related_name='trip_night_1')
    campsite_2 = models.ForeignKey('Campsite', related_name='trip_night_2')

    absolute_url_pattern = 'db:template:template_update'

    @property
    def max_num_people(self):
        """ Maximum number of people on trip: max_trippees + 2 leaders """
        return self.max_trippees + 2

    def __str__(self):
        return "{}: {}".format(self.name, self.description)

class TripType(DatabaseModel):
    
    name = models.CharField(max_length=255)
    leader_description = models.TextField()
    trippee_description = models.TextField()
    packing_list = models.TextField() # TODO: this should be inherited, somehow.
    # can we have some sort of common/base packing list? and add in extras?

    absolute_url_pattern = 'db:triptype:triptype_update'

    def __str__(self):
        return self.name

class Campsite(DatabaseModel):
    
    name = models.CharField(max_length=255)
    capacity = models.PositiveSmallIntegerField()
    directions = models.TextField()
    bugout = models.TextField() # directions for quick help/escape
    secret = models.TextField() # door codes, hidden things, other secret information

    def __str__(self):
        return self.name
