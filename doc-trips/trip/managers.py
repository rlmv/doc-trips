

from django.db import models

class SectionDatesManager(models.Manager):

    def camping_dates(self, trips_year):
        """ Get all dates when trips are out camping for trips_year """

        sections = self.filter(trips_year=trips_year)

        nights_camping = set()
        for section in sections:
            nights_camping.update(section.nights_camping)

        camping_dates = sorted(list(nights_camping))

        return camping_dates
