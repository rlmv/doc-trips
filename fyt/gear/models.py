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
    gear = models.ManyToManyField(Gear)
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

    def clean(self):
        if not (bool(self.incoming_student) ^ bool(self.volunteer)):
            raise ValidationError('A gear request must either be for an '
                                  'incoming student or a trips volunteer')

    def __str__(self):
        return 'GearRequest ({})'.format(self.user)
