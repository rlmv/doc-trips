
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured

from db.managers import TripsYearManager, CalendarManager


class TripsYear(models.Model):

    """ Global config object. Each year of trips has one such object.

    All other db objects point to their years' TripsYear.
    """

    year = models.PositiveIntegerField(unique=True, primary_key=True)
    # only one current TripsYear at any time
    is_current = models.BooleanField(default=False) 

    objects = TripsYearManager()


class DatabaseModel(models.Model):

    """ Abstract base class for all models in the trips database.

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

    @classmethod
    def get_reference_name(cls):
        """ 
        Return the canonical name by which to reference the model.
        
        Used to name urls and url namespaces. 

        This is a class method so that it can be called on the Model
        in addition to instances.
        """
        return cls._meta.verbose_name.replace(' ', '')

    @classmethod
    def get_app_name(cls):
        """ Return the app name of cls. """
        return cls._meta.app_label

        
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

    # override the default object manager
    objects = CalendarManager()

class Cost(DatabaseModel):

    cost = models.PositiveIntegerField()
