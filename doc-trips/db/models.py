
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

class CalendarManager(models.Manager):

    def calendar(self):
        
        calendar, created = self.get_or_create(id=1)
        return calendar

from django.utils import timezone

class Calendar(models.Model):
    """ 
    Singleton model for import dates
    """
    leader_application_open = models.DateTimeField(default=timezone.now)
    leader_application_closed = models.DateTimeField(default=timezone.now)

    # TODO: ??? are we going to have leader recs?
    # leader_recommendation_due = models.DateTimeField()

    leader_assignment_posted = models.DateTimeField(default=timezone.now)
    trippee_registration_open = models.DateTimeField(default=timezone.now)
    trippee_registration_closed = models.DateTimeField(default=timezone.now)
    trippee_assignment_posted = models.DateTimeField(default=timezone.now)

    migration_date = models.DateTimeField(default=timezone.now)

    objects = CalendarManager()

    def save(self, *args, **kwargs):
        self.id = 1
        super(Calendar, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass


    def is_leader_application_available(self):

        now = timezone.now()
        return (self.leader_application_open < now and
                now < self.leader_application_closed)
        
         

class Cost(DatabaseModel):

    cost = models.PositiveIntegerField()
