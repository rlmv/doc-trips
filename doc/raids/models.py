from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from doc.db.models import DatabaseModel
from doc.trips.models import Trip, Campsite


class Raid(DatabaseModel):
    """
    A raid 
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)
    trip = models.ForeignKey(Trip, null=True, blank=True)
    campsite = models.ForeignKey(Campsite, null=True, blank=True)
    date = models.DateField()
    plan = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.trip is None and self.campsite is None:
            raise ValidationError('raid must have a campsite or trip')

    def detail_url(self):
        return reverse('db:raids:detail', kwargs=self.obj_kwargs())


class Comment(DatabaseModel):
    """
    A comment on a raid.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
