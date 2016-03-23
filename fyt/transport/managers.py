from django.db import models

from fyt.utils.matrix import OrderedMatrix


class StopManager(models.Manager):

    def external(self, trips_year):
        from fyt.transport.models import Route
        EXTERNAL = Route.EXTERNAL
        return self.filter(trips_year=trips_year, route__category=EXTERNAL)


class RouteManager(models.Manager):

    def internal(self, trips_year):
        from fyt.transport.models import Route
        return self.filter(trips_year=trips_year, category=Route.INTERNAL)

    def external(self, trips_year):
        from fyt.transport.models import Route
        return self.filter(trips_year=trips_year, category=Route.EXTERNAL)


class ScheduledTransportManager(models.Manager):

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('route')

    def internal(self, trips_year):
        from fyt.transport.models import Route
        return self.filter(trips_year=trips_year, route__category=Route.INTERNAL)


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
            trip_assignment__isnull=False
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


class StopOrderManager(models.Manager):

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            'trip__template',
            'trip__section',
            'trip__template__dropoff_stop',
            'trip__template__pickup_stop',
        )
