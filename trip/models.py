

from django.db import models
from django.contrib.auth import get_user_model


class ScheduledTrip(models.Model):

    trips_year = models.PositiveIntegerField()
    template = models.ForeignKey('TripTemplate')
            
    pass



class TripTemplate(models.Model):

    trips_year = models.PositiveIntegerField()
    
    name = models.PositiveSmallIntegerField() # TODO: validate this to range [0-999]
    trip_type = models.ForeignKey('TripType')
    max_trippees = models.PositiveSmallIntegerField()
    non_swimmers_allowed = models.BooleanField(default=True)
    
    """ TODO:
    dropoff_transport_stop = models.ForeignKey('TransportStop')
    pickup_transport_stop = models.ForeignKey('TransportStop')
    """
    campsite1 = models.ForeignKey('Campsite')
    campsite2 = models.ForeignKey('Campsite')
    

class TripType(models.Model):
    
    trips_year = models.PositiveIntegerField()
    
    name = models.CharField(max_length=255)
    leader_description = models.TextField()
    trippee_description = models.TextField()
    packing_list = models.TextField() # TODO: this should be inherited, somehow.
    # can we have some sort of common/base packing list? and add in extras?


class Campsite(models.Model):

    trips_year = models.PositiveIntegerField()
    
    name = models.CharField(max_length=255)
    capacity = models.PositiveSmallIntegerField()
    directions = models.TextField()
    
    """ TODO:
    bugout
    secret
    """

