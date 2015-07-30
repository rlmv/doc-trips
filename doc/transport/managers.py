from django.db import models

from doc.utils.matrix import OrderedMatrix


class StopManager(models.Manager):

    def external(self, trips_year):
        from doc.transport.models import Route
        EXTERNAL = Route.EXTERNAL
        return self.filter(trips_year=trips_year, route__category=EXTERNAL)


class RouteManager(models.Manager):

    def internal(self, trips_year):
        from doc.transport.models import Route
        return self.filter(trips_year=trips_year, category=Route.INTERNAL)

    def external(self, trips_year):
        from doc.transport.models import Route
        return self.filter(trips_year=trips_year, category=Route.EXTERNAL)


class ScheduledTransportManager(models.Manager):

    def internal(self, trips_year):
        from doc.transport.models import Route
        return self.filter(trips_year=trips_year, route__category=Route.INTERNAL)


def external_route_matrix(trips_year, default=None):
    """ 
    Return an OrderedMatrix of [routes][sections]
    for local sections and external routes.
    """
    from doc.trips.models import Section
    from doc.transport.models import Route

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
    """
    """
    def matrix(self, trips_year):
        """ 
        Each entry in the matrix contains the number of 
        trippees riding [route] on [section].
        """
        from doc.incoming.models import IncomingStudent
        matrix = external_route_matrix(trips_year, default=0)
        passengers = IncomingStudent.objects.filter(
            trips_year=trips_year,
            bus_assignment__isnull=False,
            trip_assignment__isnull=False
        ).select_related(
            'bus_assignment__route',
            'trip_assignment__section'
        )
        for p in passengers:
            matrix[p.bus_assignment.route][p.trip_assignment.section] += 1

        return matrix


class StopOrderManager(models.Manager):
    
    def get_queryset(self):
        qs = super(StopOrderManager, self).get_queryset()
        return qs.select_related(
            'trip__template',
            'trip__section',
            'trip__template__dropoff',
            'trip__template__pickup',
        )
