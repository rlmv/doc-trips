
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured

from doc.db.managers import TripsYearManager


class TripsYear(models.Model):

    """ Global config object. Each year of trips has one such object.

    All other db objects point to their years' TripsYear.

    TODO: validate that there is only one object with is_current=True
    """

    year = models.PositiveIntegerField(unique=True, primary_key=True)
    # only one current TripsYear at any time
    is_current = models.BooleanField(default=False) 

    objects = TripsYearManager()

    def __str__(self):
        return str(self.year)


class DatabaseModel(models.Model):
    """ 
    Abstract base class for all models in the trips database.

    Manages the trips_year property.

    TODO: rename this to TripsModel?
    """

    # TODO: index on trips_year?
    trips_year = models.ForeignKey('TripsYear', editable=False, on_delete=models.PROTECT) 

    class Meta:
        abstract = True

    def get_absolute_url(self):
        from doc.db.urlhelpers import reverse_detail_url
        return reverse_detail_url(self)

    @classmethod
    def get_model_name(cls):
        """ Return the name of the model. """
        return cls.__name__

    @classmethod
    def get_model_name_lower(cls):
        """ Lowercased name of the model. """
        return cls.get_model_name().lower()

    @classmethod
    def get_app_name(cls):
        """ Return the app name of cls. """
        return cls._meta.app_label
         
