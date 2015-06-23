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


class ExternalTransportManager(models.Manager):
    """ 
    Manager for the ExternalTransport model.
    """
    def schedule_matrix(self, trips_year):
        """
        Returns and ordered matrix of all scheduled external
        transports.
        """
        from doc.trips.models import Section
        from doc.transport.models import Route
        
        rts = Route.objects.external(trips_year)
        sxns = Section.objects.local(trips_year)
        matrix = OrderedMatrix(rts, sxns)

        scheduled = self.filter(trips_year=trips_year)
        for transport in scheduled:
            matrix[transport.route][transport.section] = transport
        return matrix
        

    
