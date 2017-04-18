
from django.db import models
from django.core.urlresolvers import reverse

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
        ordering = ['start_time']

    training = models.ForeignKey(Training, on_delete=models.PROTECT)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def registered_emails(self):
        """Emails for all registered attendees."""
        return self.registered.values_list(
            'volunteer__applicant__email', flat=True)

    # TODO: move to view
    def registered_emails_str(self):
        return "; ".join(self.registered_emails())

    def __str__(self):
        return "{}: {}, {} to {}".format(
            self.training,
            self.date.strftime('%B %d'),
            self.start_time.strftime('%l:%M %p'),
            self.end_time.strftime('%l:%M %p'))

    def update_attendance_url(self):
        return reverse('db:session:update_attendance',
                       kwargs=self.obj_kwargs())


class Attendee(DatabaseModel):
    """
    A volunteer attending trainings.
    """
    volunteer = models.OneToOneField(Volunteer)
    registered_sessions = models.ManyToManyField(
        Session, blank=True, related_name='registered')
    complete_sessions = models.ManyToManyField(
        Session, blank=True, related_name='completed')

    def __str__(self):
        return str(self.volunteer)

    def training_complete(self):
        """
        A volunteer has completed all trainings if they attended a session
        for each type of training.
        """
        trainings = Training.objects.filter(trips_year=self.trips_year)
        complete = [s.training for s in self.complete_sessions.all()]

        return not set(trainings) - set(complete)

    def detail_url(self):
        return self.volunteer.detail_url()
