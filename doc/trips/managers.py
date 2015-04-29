
from django.db import models

from doc.utils.matrix import make_ordered_matrix


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
        

class ScheduledTripManager(models.Manager):

    def matrix(self, trips_year):
        """
        Return a matrix of scheduled trips.

        matrix[template][section] gives the scheduled trip
        with template and section, or None if it is not scheduled.

        Returns OrderedDicts so that you can iterate over the keys:
        >>> for template in matrix:
        >>>    for section in matrix[template]:
        >>>        ...
        """

        from doc.trips.models import Section, TripTemplate
        sections = Section.objects.filter(trips_year=trips_year)
        templates = (
            TripTemplate.objects.filter(trips_year=trips_year)
            .select_related('triptype')
        )

        matrix = make_ordered_matrix(templates, sections)

        # see https://docs.djangoproject.com/en/dev/ref/models/querysets/#id7
        # http://stackoverflow.com/questions/6795202/django-count-in-multiple-annotations
        trips = (self.filter(trips_year=trips_year)
                 .select_related('section', 'template')
                 .annotate(num_trippees=models.Count('trippees', distinct=True))
                 .annotate(num_leaders=models.Count('leaders', distinct=True)))
        
        for trip in trips:
            matrix[trip.template][trip.section] = trip

        return matrix
        
