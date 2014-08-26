
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

    absolute_url_pattern = None

    def get_absolute_url(self):
        """ Get the absolute url for database objects. 

        Uses the url namespace string specified in absolute_url_pattern
        to perform a reverse lookup. This is mostly used by class based 
        views, and can be overridden if necessary.

        """
        if not self.absolute_url_pattern:
            msg = ("%s must define 'absolute_url_pattern' or override "
                  "'get_absolute_url' to reverse absolute url")
            raise ImproperlyConfigured(msg % self.__class__.__name__)

        # Using _id instead of .pk saves a database hit. See goo.gl/REX06L
        kwargs = {'trips_year': self.trips_year_id, 'pk': self.pk}
        return reverse(self.absolute_url_pattern, kwargs=kwargs)

    def save(self, *args, **kwargs):
        """ Attach the current trips_year to new database objects.
        
        If trips_year is explicitly specified, use that year instead. 
        This overrides the default model save method.
        """
        if self.pk is None and not hasattr(self, 'trips_year'):
            self.trips_year = TripsYear.objects.current()
            
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

    # override the default object manager
    objects = CalendarManager()

class Cost(DatabaseModel):

    cost = models.PositiveIntegerField()
