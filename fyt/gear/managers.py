from django.db import models

from fyt.utils.matrix import OrderedMatrix


class GearRequestManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('incoming_student', 'volunteer')

    def matrix(self, trips_year):
        from .models import Gear

        requests = self.filter(trips_year=trips_year).prefetch_related(
            'gear', 'provided'
        )
        equipment = Gear.objects.filter(trips_year=trips_year)

        matrix = OrderedMatrix(requests, equipment, default=False)
        for request in requests:
            for gear in request.gear.all():
                matrix[request][gear] = True

        return matrix
