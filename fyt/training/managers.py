from django.db import models
from django.db.models import Q


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

    def first_aid_complete(self, trips_year):
        """
        All volunteers with first aid certifications.
        """
        return self.filter(
            trips_year=trips_year
        ).exclude(
            Q(fa_cert='') & Q(fa_other='')
        )

    def first_aid_incomplete(self, trips_year):
        """
        All volunteers missing first aid certifications.
        """
        return self.filter(
            trips_year=trips_year
        ).filter(
            fa_cert='', fa_other=''
        )
