from datetime import timedelta

from django.db import models
from django.db.models import F, Q

from fyt.utils.matrix import OrderedMatrix
from fyt.trips.constants import FIRST_CAMPSITE_DELTA, LODGE_ARRIVAL_DELTA, RETURN_TO_CAMPUS_DELTA


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

    def leader_dates(self, trips_year):
        sections = self.filter(trips_year=trips_year)
        dates = set()
        for section in sections:
            dates.update(section.leader_dates)
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

    def sophomore_leaders_ok(self, trips_year):
        return self.filter(trips_year=trips_year, sophomore_leaders_ok=True)


class TripManager(models.Manager):
    def get_queryset(self):
        """
        Go ahead and pull in section and template since we
        use them with basically every queryset.
        """
        qs = super().get_queryset()
        return qs.select_related('section', 'template')

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

        from fyt.trips.models import Section, TripTemplate

        sections = Section.objects.filter(trips_year=trips_year)
        templates = TripTemplate.objects.filter(trips_year=trips_year).select_related(
            'triptype'
        )

        matrix = OrderedMatrix(templates, sections)

        # see https://docs.djangoproject.com/en/dev/ref/models/querysets/#id7
        # http://stackoverflow.com/questions/6795202/django-count-in-multiple-annotations
        trips = self.with_counts(trips_year)

        for trip in trips:
            matrix[trip.template][trip.section] = trip

        return matrix

    def with_counts(self, trips_year):
        """
        Annotate the number of trippees and leaders.
        """
        return (
            self.filter(trips_year=trips_year)
            .annotate(num_trippees=models.Count('trippees', distinct=True))
            .annotate(num_leaders=models.Count('leaders', distinct=True))
            .annotate(size=F('num_trippees') + F('num_leaders'))
            # Silence deprecation warning caused by
            # https://docs.djangoproject.com/en/2.2/releases/2.2/#model-meta-ordering-will-no-longer-affect-group-by-queries
            .order_by(*self.model._meta.ordering)
        )

    def dropoffs(self, route, date, trips_year):
        """
        All trips which are dropped off on route on date

        This returns all trips which have overridden the dropoff
        route, or whose template drops off with this route.
        """

        return (
            self.with_counts(trips_year)
            .filter(section__leaders_arrive=date - timedelta(days=FIRST_CAMPSITE_DELTA))
            .filter(
                Q(dropoff_route=route)
                | Q(dropoff_route=None, template__dropoff_stop__route=route)
            )
        )

    def pickups(self, route, date, trips_year):
        """
        All trips which are picked up on route and taken to the lodge on date.
        """
        return (
            self.with_counts(trips_year)
            .filter(section__leaders_arrive=date - timedelta(days=LODGE_ARRIVAL_DELTA))
            .filter(
                Q(pickup_route=route)
                | Q(pickup_route=None, template__pickup_stop__route=route)
            )
        )

    def returns(self, route, date, trips_year):
        """
        All trips which return to campus via route on date.
        """
        return (
            self.with_counts(trips_year)
            .filter(section__leaders_arrive=date - timedelta(days=RETURN_TO_CAMPUS_DELTA))
            .filter(
                Q(return_route=route)
                | Q(return_route=None, template__return_route=route)
            )
        )


class CampsiteManager(models.Manager):
    def matrix(self, trips_year):
        """
        Return of a matrix of trips residency by date.

        matrix[campsite][date] is a list of all trips staying
        at campsite on date.
        """
        from .models import Section, Trip

        campsites = self.filter(trips_year=trips_year)
        dates = Section.dates.camping_dates(trips_year)

        matrix = OrderedMatrix(campsites, dates, default=list)

        trips = Trip.objects.filter(trips_year=trips_year).select_related(
            'template__campsite1', 'template__campsite2'
        )

        for trip in trips:
            matrix[trip.template.campsite1][trip.section.at_campsite1].append(trip)
            matrix[trip.template.campsite2][trip.section.at_campsite2].append(trip)

        return matrix


class TripTypeManager(models.Manager):
    def visible(self, trips_year):
        """
        Return the triptypes which are not hidden from leader applications and
        incoming student registrations.
        """
        return self.filter(trips_year=trips_year, hidden=False)
