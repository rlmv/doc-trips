

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

    def trip_dates(self, trips_year):
        """ 
        Get all dates when trips are happening this trips_year.

        Excludes day 0 when leaders arrive for training.
        """

        sections = self.filter(trips_year=trips_year)
        dates = set()
        for section in sections:
            dates.update(section.trip_dates)
        return sorted(list(dates))


class SectionManager(models.Manager):

    def local(self, trips_year):
        return self.filter(trips_year=trips_year, is_local=True)

    def not_local(self, trips_year):
        return self.filter(trips_year=trips_year, is_local=False)
        
    def international(self, trips_year):
        return self.filter(trips_year=trips_year, is_international=True)

    def transfer(self, trips_year):
        return self.filter(trips_year=trips_year, is_transfer=True)
        
    def native(self, trips_year):
        return self.filter(trips_year=trips_year, is_native=True)
        
    def fysep(self, trips_year):
        return self.filter(trips_year=trips_year, is_fysep=True)

    def exchange(self, trips_year):
        return self.filter(trips_year=trips_year, is_exchange=True)
        
