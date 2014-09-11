
from django.db import models

# TODO: test cases

class TripsYearManager(models.Manager):
    """ Object manager for TripsYear """

    def current(self):
        """ 
        Get the current TripsYear object. 

        current refers to the year of trips, eg. Trips 2014, 
        not *necessarily* the actual date.
        """
        return self.get(is_current=True)



