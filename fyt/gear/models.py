from django.core.exceptions import ValidationError
from django.db import models

from fyt.applications.models import Volunteer
from fyt.core.models import DatabaseModel
from fyt.incoming.models import IncomingStudent
from fyt.users.models import DartmouthUser


class Gear(DatabaseModel):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class GearRequest(DatabaseModel):
    """
    A gear request is either attached to an IncomingStudent, or to a Volunteer.
    """
    gear = models.ManyToManyField(Gear, blank=True)
    additional = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    incoming_student = models.OneToOneField(
        IncomingStudent,
        editable=False,
        null=True,
        on_delete=models.PROTECT)

    volunteer = models.OneToOneField(
        Volunteer,
        editable=False,
        null=True,
        on_delete=models.PROTECT)

    @property
    def requester(self):
        return self.incoming_student or self.volunteer

    @requester.setter
    def requester(self, user):
        try:
            self.incoming_student = IncomingStudent.objects.get(
                trips_year=self.trips_year, netid=user.netid)
        except IncomingStudent.DoesNotExist:
            pass
        try:
            self.volunteer = Volunteer.objects.get(
                trips_year=self.trips_year, applicant=user)
        except Volunteer.DoesNotExist:
            pass

    def clean(self):
        if self.incoming_student and self.volunteer:
            raise ValidationError('Only incoming students and trips volunteers '
                                  'may request gear.')

        if not self.incoming_student and not self.volunteer:
            raise ValidationError('Only incoming students and trips volunteers '
                                  'may request gear.')

    def __str__(self):
        return 'GearRequest ({})'.format(self.user)
