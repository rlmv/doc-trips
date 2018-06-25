from django.db import models

from fyt.core.models import DatabaseModel
from fyt.users.models import DartmouthUser


class Gear(DatabaseModel):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class GearRequest(DatabaseModel):
    user = models.ForeignKey(DartmouthUser, editable=False,
                             on_delete=models.PROTECT)
    gear = models.ManyToManyField(Gear)
    additional = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'GearRequest ({})'.format(self.user)
