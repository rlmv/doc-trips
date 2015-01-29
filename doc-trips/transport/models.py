
from django.db import models

from db.models import DatabaseModel

TRANSPORT_CATEGORIES = (
    ('INTERNAL', 'Internal'),
    ('EXTERNAL', 'External'),
)

class Stop(DatabaseModel):

    name = models.CharField(max_length=255)
    # TODO: validate that lat and long are interdependet / location is there?
    location = models.CharField(max_length=255, help_text='Plain text address, eg. Hanover, NH 03755. This must take you to the location in Google maps.')
    latitude = models.FloatField()
    longitude = models.FloatField()

    # verbal directions, descriptions. migrated from legacy.
    directions = models.TextField()

    #TODO: validate category against route's category.
    # OR: get rid of category entirely?
    route = models.ForeignKey('Route')
    category = models.CharField(max_length=20, choices=TRANSPORT_CATEGORIES)

    # TODO: validate that this only is used if category==EXTERNAL
    cost = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # legacy data from old db - hide on site?
    distance = models.IntegerField()

    # mostly used for external routes
    pickup_time = models.TimeField(blank=True, null=True)
    dropoff_time = models.TimeField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    
class Route(DatabaseModel):

    name = models.CharField(max_length=255)
    vehicle = models.ForeignKey('Vehicle')
    category = models.CharField(max_length=20, choices=TRANSPORT_CATEGORIES)

    def __str__(self):
        return self.name
    

class Vehicle(DatabaseModel):
    # eg. Internal Bus, Microbus, 
    name = models.CharField(max_length=255)
    capacity = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class ScheduledTransportation(DatabaseModel):

    route = models.ForeignKey('Route')
    date = models.DateField()
    
    
    
    
    
