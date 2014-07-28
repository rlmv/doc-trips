
from django.db import models
from django.conf import settings


class TripsYear(models.Model):

    """ Global config object. Each year of trips has one such object.

    All other db objects point to their years' TripsYear.
    """
    
    year = models.PositiveIntegerField(unique=True, primary_key=True)
    is_current = models.BooleanField(default=False) # only one current TripsYear at any time


class TripsYearAccessor:
    
    """ Global acccessor for the current trips year. 

    TODO: move this into a better named module.
    """
    
    @property
    def current(self):
        """ Get the current TripsYear object. """
        return TripsYear.objects.get(is_current=True)



trips_year = TripsYearAccessor()

class CalendarAccessor:

    """ Global accessor for important dates. """

    @property
    def current(self):
        """ Get the current Calendar object"""
        return Calendar.objects.get(trips_year=trips_year.current)

calendar = CalendarAccessor()


class DatabaseModel(models.Model):

    """ Abstract base class for all models in the database.

    Manages the trips_year property. Whenever a DatabaseModel is created,
    the current trips_year is automatically attached to the object if it is
    not already. 
    
    See https://docs.djangoproject.com/en/dev/topics/db/models/#abstract-base-classes
    """
    
    # TODO: index on trips_year?
    # editable=False hides this field in all forms
    trips_year = models.ForeignKey('TripsYear', editable=False) 

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """ When an new object is created, attach current trips_year.

        This overrides the default model save method.
        """
        
        # TODO: should this check whether trips_year is already set?
        if self.pk is None: # created
            self.trips_year = trips_year.current
            
        super(DatabaseModel, self).save(*args, **kwargs)


class Calendar(DatabaseModel):

    # trips_year is inherited from DatabaseModel

    leader_application_available = models.DateTimeField()
    leader_application_due = models.DateTimeField()
    # TODO: ??? are we going to have leader recs?
    # leader_recommendation_due = models.DateTimeField()
    leader_assignment_posted = models.DateTimeField()
    trippee_registration_available = models.DateTimeField()
    trippee_assignment_posted = models.DateTimeField()

    migration_date = models.DateTimeField()



class Cost(DatabaseModel):

    cost = models.PositiveIntegerField()
