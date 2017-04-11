
from django.db import models

from fyt.db.models import DatabaseModel


class Training(DatabaseModel):
    """
    A type of training.
    """
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Session(DatabaseModel):
    """
    A scheduled session for a certain training type.
    """
    class Meta:
        ordering = ['time']

    training = models.ForeignKey(Training)
    time = models.DateTimeField()
    duration = models.DurationField()

    def __str__(self):
        return "{}: {}".format(self.training, self.time)

#
# class Signup(DatabaseModel):
#     """
#     A user's registration for a particular training session.
#     """
#     volunteer = models.ForeignKey(Volunteer)
#     session = models.ForeignKey(Session)
