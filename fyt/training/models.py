
from django.db import models

from fyt.applications.models import Volunteer
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

    training = models.ForeignKey(Training, on_delete=models.PROTECT)
    time = models.DateTimeField()
    duration = models.DurationField()

    def attendee_emails(self):
        """Emails for all registered attendees."""
        return self.attendee_set.values_list(
            'volunteer__applicant__email', flat=True)

    # TODO: move to view
    def attendee_emails_str(self):
        return "; ".join(self.attendee_emails())

    def __str__(self):
        return "{}: {}".format(self.training,
                               self.time.strftime('%x %H:%M'))


class Attendee(DatabaseModel):
    """
    A volunteer attending trainings.
    """
    volunteer = models.OneToOneField(Volunteer)
    sessions = models.ManyToManyField(Session, blank=True)

    def __str__(self):
        return str(self.volunteer)

    def detail_url(self):
        return self.volunteer.detail_url()
