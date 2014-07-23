

from django.db import models
from django.contrib.auth import get_user_model


class ScheduledTrip(models.Model):

    trips_year = models.PositiveIntegerField()
    template = models.ForeignKey('TripTemplate')
    section = models.ForeignKey('Section')

    # The leaders for this trip can be selected with the 'leaders' field.
    # See LeaderApplication.assigned_trip.
            
    def __str__(self):
        # TODO: add section info
        return str(self.template)


class Section(models.Model):
    
    """ Model to represent a trips section. """

    trips_year = models.PositiveIntegerField()
    name = models.CharField(max_length=1) # A,B,C, etc
    leaders_arrive = models.DateTimeField()
    
    is_local = models.BooleanField(default=False)
    is_exchange = models.BooleanField(default=False)
    is_transfer = models.BooleanField(default=False)
    is_international = models.BooleanField(default=False)
    is_fysep = models.BooleanField(default=False)
    is_native = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TripTemplate(models.Model):

    trips_year = models.PositiveIntegerField()
    
    name = models.PositiveSmallIntegerField() # TODO: validate this to range [0-999]
    description = models.CharField(max_length=255) # short info

    trip_type = models.ForeignKey('TripType')
    max_trippees = models.PositiveSmallIntegerField()
    non_swimmers_allowed = models.BooleanField(default=True)
    
    """ TODO:
    dropoff_transport_stop = models.ForeignKey('TransportStop')
    pickup_transport_stop = models.ForeignKey('TransportStop')
    """
    campsite_1 = models.ForeignKey('Campsite', related_name='trip_night_1')
    campsite_2 = models.ForeignKey('Campsite', related_name='trip_night_2')

    def __str__(self):
        return "{}: {}".format(self.name, self.description)

class TripType(models.Model):
    
    trips_year = models.PositiveIntegerField()
    
    name = models.CharField(max_length=255)
    leader_description = models.TextField()
    trippee_description = models.TextField()
    packing_list = models.TextField() # TODO: this should be inherited, somehow.
    # can we have some sort of common/base packing list? and add in extras?

    def __str__(self):
        return self.name


class Campsite(models.Model):

    trips_year = models.PositiveIntegerField()
    
    name = models.CharField(max_length=255)
    capacity = models.PositiveSmallIntegerField()
    directions = models.TextField()
    
    """ TODO:
    bugout
    secret
    """

    def __str__(self):
        return self.name
