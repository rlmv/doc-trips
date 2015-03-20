

from django.db import models

class SectionDatesManager(models.Manager):

    def camping_dates(self, trips_year):
        """ 
        Get all dates when trips are out camping for this trips_year.

        Return a sorted list of dates.
        """

        sections = self.filter(trips_year=trips_year)

        nights_camping = set()
        for section in sections:
            nights_camping.update(section.nights_camping)

        return sorted(list(nights_camping))


class SectionManager(models.Manager):

    def local(self, trips_year):
        return self.filter(trips_year=trips_year, is_local=True)

    def not_local(self, trips_year):
        return self.filter(trips_year=trips_year, is_local=False)
        
    def international(self, trips_year):
        return self.filter(trips_year=trips_year, is_international=True)
