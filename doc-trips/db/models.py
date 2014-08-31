
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


    def get_update_url(self):
        """ Get the absolute url for database objects. 

        Use the verbose_name of the model to to a namespace lookup.
        """
        
        name = self.get_reference_name()
        url_pattern = '{0}:{1}:{1}_update'.format('db', name) 
        
        """
        if not self.absolute_url_pattern:
            msg = ("%s must define 'absolute_url_pattern' or override "
                  "'get_absolute_url' to reverse absolute url")
            raise ImproperlyConfigured(msg % self.__class__.__vname__)
        """
        # Using _id instead of .pk saves a database hit. See goo.gl/REX06L
        kwargs = {'trips_year': self.trips_year_id, 'pk': self.pk}
        return reverse(url_pattern, kwargs=kwargs)

    def get_absolute_url(self):
        """ TODO: use a DetailView as target, or stick with update? """
        return self.get_update_url()

    def get_delete_url(self):
        """  Get the canonical url to delete this object """
        name = self.get_reference_name()
        url_pattern = '{0}:{1}:{1}_delete'.format('db', name)

        kwargs = {'trips_year': self.trips_year_id, 'pk': self.pk}
        return reverse(url_pattern, kwargs=kwargs)

    @classmethod
    def get_create_url(cls, trips_year):
        """ Return the canonical url to create an object of cls """
        
        # TODO: extract 'db' from a class attribute, eg 'db_namespace'?
        name = cls.get_reference_name()
        url_pattern = '{0}:{1}:{1}_create'.format('db', name)

        kwargs = {'trips_year': trips_year.pk}
        return reverse(url_pattern, kwargs=kwargs)


    @classmethod
    def get_reference_name(cls):
        """ Return the canonical name by which to reference the model
        
        Used to name urls and url namespaces. 

        This is a class method so that it can be called on the Model
        in addition to instances.
        """
        return cls._meta.verbose_name.replace(' ', '')

    @classmethod
    def get_app_name(cls):
        """ Return the app name of cls """
        return cls._meta.app_label

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
