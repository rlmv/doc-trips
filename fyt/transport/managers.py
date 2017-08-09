from django.db import models
from django.db.models import Q

from fyt.transport.category import EXTERNAL, INTERNAL
from fyt.utils.matrix import OrderedMatrix


class StopManager(models.Manager):

    def external(self, trips_year):
        return self.filter(trips_year=trips_year, route__category=EXTERNAL)


class RouteManager(models.Manager):

    def internal(self, trips_year):
        return self.filter(trips_year=trips_year, category=INTERNAL)

    def external(self, trips_year):
        return self.filter(trips_year=trips_year, category=EXTERNAL)


class InternalBusManager(models.Manager):

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('route')

    def internal(self, trips_year):
        return self.filter(trips_year=trips_year, route__category=INTERNAL)

    def validate(self):
        for bus in self.order_by('trips_year'):
            bus.validate_stop_ordering()
            print(f'validated {bus}')


def external_route_matrix(trips_year, default=None):
    """
    Return an OrderedMatrix of [routes][sections]
    for local sections and external routes.
    """
    from fyt.trips.models import Section
    from fyt.transport.models import Route

    rts = Route.objects.external(trips_year)
    sxns = Section.objects.local(trips_year)
    return OrderedMatrix(rts, sxns, default=default)


class ExternalBusManager(models.Manager):
    """
    Manager for the ExternalBus model.
    """
    def schedule_matrix(self, trips_year):
        """
        Returns and ordered matrix of all scheduled external
        transports.
        """
        matrix = external_route_matrix(trips_year)
        scheduled = self.filter(
            trips_year=trips_year
        ).select_related(
            'route', 'section'
        )
        for transport in scheduled:
            matrix[transport.route][transport.section] = transport
        return matrix


class ExternalPassengerManager(models.Manager):

    def matrix_to_hanover(self, trips_year):
        """
        Each entry in the matrix contains the number of
        trippees riding [route] on [section] TO Hanover.
        """
        return self._matrix(
            trips_year,
            (models.Q(bus_assignment_round_trip__isnull=False) |
             models.Q(bus_assignment_to_hanover__isnull=False)),
            lambda p: p.bus_assignment_to_hanover
        )

    def matrix_from_hanover(self, trips_year):
        """
        Each entry in the matrix contains the number of
        trippees riding [route] on [section] FROM Hanover.
        """
        return self._matrix(
            trips_year,
            (models.Q(bus_assignment_round_trip__isnull=False) |
             models.Q(bus_assignment_from_hanover__isnull=False)),
            lambda p: p.bus_assignment_from_hanover
        )

    def _matrix(self, trips_year, condition, getter):
        """
        getter returns the one-way bus stop from the IncStudent
        """
        from fyt.incoming.models import IncomingStudent
        matrix = external_route_matrix(trips_year, default=0)
        passengers = IncomingStudent.objects.filter(
            condition,
            trips_year=trips_year,
            trip_assignment__isnull=False,
            trip_assignment__section__is_local=True
        ).select_related(
            'bus_assignment_round_trip__route',
            'bus_assignment_to_hanover__route',
            'bus_assignment_from_hanover__route',
            'trip_assignment__section'
        )
        for p in passengers:
            bus = p.bus_assignment_round_trip or getter(p)
            matrix[bus.route][p.trip_assignment.section] += 1

        return matrix

    def invalid_riders(self, trips_year):
        """
        Returns all IncomingStudents who are assigned to a local bus but who
        are either not assigned to a trip or are assigned to a non-local
        section.
        """
        from fyt.incoming.models import IncomingStudent
        return IncomingStudent.objects.filter(
            Q(bus_assignment_round_trip__isnull=False) |
            Q(bus_assignment_to_hanover__isnull=False) |
            Q(bus_assignment_from_hanover__isnull=False),
            Q(trip_assignment=None) |
            Q(trip_assignment__section__is_local=False),
            trips_year=trips_year)


class StopOrderManager(models.Manager):

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            'trip__template',
            'trip__section',
            'trip__template__dropoff_stop',
            'trip__template__pickup_stop',
        )
