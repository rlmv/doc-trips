
from django.db import models

# TODO: test cases

class TripsYearManager(models.Manager):
    """ Object manager for TripsYear """

    def current(self):
        """ Get the current TripsYear object. 

        current refers to the year of trips, eg. Trips 2014, 
        not *necessarily* the actual date.
        """
        return self.model.objects.get(is_current=True)


class CalendarManager(models.Manager):
    """ Object manager for the Calendar class """

    def current(self):
        """ Get the current Calendar object"""

        # get_model prevents circular dependency
        TripsYear = models.get_model('db', 'TripsYear')
        Calendar = self.model

        return Calendar.objects.get(trips_year=TripsYear.objects.current())

