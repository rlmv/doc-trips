

from django.db import models


class StopManager(models.Manager):

    def external(self, trips_year):
        return self.filter(trips_year=trips_year, route__category='EXTERNAL')
