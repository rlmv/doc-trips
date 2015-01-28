
from django.db import models

from db.models import DatabaseModel

class Stop(DatabaseModel):

    # TODO: validate that lat and long are interdependet / location is there?
    location = models.CharField(max_length=255, help_text='Plain text address, eg. Hanover, NH 03755. This must take you to the location in Google maps.')
    latitude = models.FloatField()
    longitude = models.FloatField()

    primary_route = models.ForeignKey('Route')
    
    
class Route(DatabaseModel):
    
    vehicle = models.ForeignKey('Vehicle')
    

class Vehicle(DatabaseModel):
    # eg. Internal Bus, Microbus, 
    name = models.CharField(max_length=255)
    capacity = models.PositiveSmallIntegerField()


class ScheduledTransport(DatabaseModel):

    route = models.ForeignKey('Route')
    
    
    
    
    
