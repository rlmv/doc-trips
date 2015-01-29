
from django.db import models

from db.models import DatabaseModel

TRANSPORT_CATEGORIES = (
    ('INTERNAL', 'Internal'),
    ('EXTERNAL', 'External'),
    ('BOTH', 'Both'),
)

class Stop(DatabaseModel):

    class Meta:
        ordering = ['category', 'name']

    name = models.CharField(max_length=255)
    # TODO: validate that lat and long are interdependet / location is there?
    address = models.CharField(max_length=255, help_text='Plain text address, eg. Hanover, NH 03755. This must take you to the location in Google maps.')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    # verbal directions, descriptions. migrated from legacy.
    directions = models.TextField()

    #TODO: validate category against route's category.
    # OR: get rid of category entirely?
    route = models.ForeignKey('Route', null=True)
    category = models.CharField(max_length=20, choices=TRANSPORT_CATEGORIES)

    # TODO: validate that this only is used if category==EXTERNAL
    cost = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # legacy data from old db - hide on site?
    distance = models.IntegerField(null=True)

    # mostly used for external routes
    pickup_time = models.TimeField(blank=True, null=True)
    dropoff_time = models.TimeField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    
class Route(DatabaseModel):

    name = models.CharField(max_length=255)
    vehicle = models.ForeignKey('Vehicle')
    category = models.CharField(max_length=20, choices=TRANSPORT_CATEGORIES)

    class Meta:
        ordering = ['category', 'vehicle', 'name']

    def __str__(self):
        return self.name
    

class Vehicle(DatabaseModel):

    # eg. Internal Bus, Microbus, 
    name = models.CharField(max_length=255)
    capacity = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ScheduledTransportation(DatabaseModel):

    route = models.ForeignKey('Route')
    date = models.DateField()
    
    
    
    
    
