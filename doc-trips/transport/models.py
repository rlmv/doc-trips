
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

    #TODO: validate category against route's category.
    # OR: get rid of category entirely?
    route = models.ForeignKey('Route')
    category = models.CharField(max_length=20, choices=TRANSPORT_CATEGORIES)

    def __str__(self):
        return self.name
        
    
    
class Route(DatabaseModel):
    
    vehicle = models.ForeignKey('Vehicle')
    category = models.CharField(max_length=20, choices=TRANSPORT_CATEGORIES)
    

class Vehicle(DatabaseModel):
    # eg. Internal Bus, Microbus, 
    name = models.CharField(max_length=255)
    capacity = models.PositiveSmallIntegerField()


class ScheduledTransportation(DatabaseModel):

    route = models.ForeignKey('Route')
    date = models.DateField()
    
    
    
    
    
