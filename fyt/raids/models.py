from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models

from fyt.db.models import DatabaseModel
from fyt.trips.models import Campsite, Trip


class Raid(DatabaseModel):
    """
    A raid 
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)
    trip = models.ForeignKey(Trip, null=True, blank=True)
    campsite = models.ForeignKey(Campsite, null=True, blank=True)
    date = models.DateField()
    plan = models.TextField(blank=True, help_text=(
        "Do you have a theme? Are you going to intercept "
        "the trip on the trail or at their campsite?"
    ))
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def clean(self):
        if self.trip is None and self.campsite is None:
            raise ValidationError('raid must have a campsite or trip')

    def detail_url(self):
        return reverse('db:raids:detail', kwargs=self.obj_kwargs())

    def delete_url(self):
        return reverse('db:raids:delete', kwargs=self.obj_kwargs())

    def __str__(self):
        return "%s %s" % (self.user, self.date.strftime('%m/%d'))

    def verbose_str(self):
        if self.trip:
            return "%s on %s" % (
                self.trip.verbose_str(),
                self.date.strftime('%m/%d')
            )


class Comment(DatabaseModel):
    """
    A comment on a raid.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)
    raid = models.ForeignKey(Raid, editable=False)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return "%s: %s" % (self.user, self.comment)


class RaidInfo(DatabaseModel):
    """
    Raid information
    """

    instructions = models.TextField()

    class Meta:
        unique_together = ['trips_year']
