
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured

from db.managers import TripsYearManager


class TripsYear(models.Model):

    """ Global config object. Each year of trips has one such object.

    All other db objects point to their years' TripsYear.

    TODO: validate that there is only one object with is_current=True
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

    def save(self, *args, **kwargs):
        """
        Attach the current trips_year to new database objects.
        
        If trips_year is explicitly specified, use that year instead. 
        This overrides the default model save method.
        """
        if self.pk is None and not hasattr(self, 'trips_year'):
            self.trips_year = TripsYear.objects.current()

        super(DatabaseModel, self).save(*args, **kwargs)


    def get_absolute_url(self):
        from db.urls import get_detail_url
        return get_detail_url(self)

    @classmethod
    def get_reference_name(cls):
        return cls.get_model_name()

    @classmethod
    def get_model_name(cls):
        """ Return the lowercase name of the model. """
        return cls.__name__.lower()

    @classmethod
    def get_app_name(cls):
        """ Return the app name of cls. """
        return cls._meta.app_label
         

class Cost(DatabaseModel):

    cost = models.PositiveIntegerField()
