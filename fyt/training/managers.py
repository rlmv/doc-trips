from django.db import models


class AttendeeManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related(
            'volunteer', 'volunteer__applicant')

    def trainable(self, trips_year):
        """
        All volunteers can be trained this year.
        """
        return self.filter(
            trips_year=trips_year
        ).filter(
            volunteer__status__in=self.model.TRAINABLE_STATUSES
        )
