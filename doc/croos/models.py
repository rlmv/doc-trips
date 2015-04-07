
from django.db import models

from doc.db.models import DatabaseModel, TripsYear


class Croo(DatabaseModel):
    """
    Represents a croo organization. 

    Migrates each year.
    """
    
    class Meta:
        ordering = ['name']
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    # TODO: croo head?

    def __str__(self):
        return self.name
    
