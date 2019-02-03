from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


"""
Our calendar is represented by a singleton Timetable object which
maintains all important trips dates.

The timetable's id is TIMETABLE_ID. We override the model save
method to only use this id, and delete to prevent deletion of
the object.
"""

TIMETABLE_ID = 1
# Number of minutes applications stay open after the posted deadline
GRACE_PERIOD = timedelta(minutes=15)


class TimetableManager(models.Manager):
    def timetable(self):
        return self.get(id=TIMETABLE_ID)


class Timetable(models.Model):
    """
    Singleton model for important dates
    """

    applications_open = models.DateTimeField(default=timezone.now)
    applications_close = models.DateTimeField(default=timezone.now)

    scoring_available = models.BooleanField(
        default=False,
        help_text=(
            "Turn this on to begin the scoring process. Only do so once all "
            "applications have been submitted. Applications with extensions "
            "will not be scored until the extension deadline has passed. "
            "Graders will have access to the scoring page when this is enabled."
        ),
    )
    hide_volunteer_page = models.BooleanField(
        default=False,
        help_text=(
            "Enabling this will hide the database Volunteers page from "
            "everyone except directors and trip leader trainers. Use "
            "this during grading to prevent graders from seeing "
            "applicant's scores."
        ),
    )
    application_status_available = models.BooleanField(
        default=False,
        help_text=(
            "Turn this on once all decisions have been made "
            "regarding Leaders and Croos"
        ),
    )
    leader_assignment_available = models.BooleanField(
        default=False,
        help_text=(
            "Turn this on to let Trip Leaders see information "
            "about their assigned trip"
        ),
    )
    trippee_registrations_open = models.DateTimeField(default=timezone.now)
    trippee_registrations_close = models.DateTimeField(default=timezone.now)
    trippee_assignment_available = models.BooleanField(
        default=False,
        help_text=("Turn this on to let Incoming Students see their trip assignments"),
    )

    objects = TimetableManager()

    def save(self, *args, **kwargs):
        self.id = TIMETABLE_ID
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    def clean(self):
        if self.applications_available() and self.scoring_available:
            raise ValidationError(
                'Scoring is not available while ' 'applications are still open'
            )

    def applications_available(self):
        """
        Are Croo and Leader applications available?

        Users can still submit an application 15 minutes after the posted
        deadline. This keeps people from losing data when they try and submit
        at the very last minute.
        """
        now = timezone.now()
        return (
            self.applications_open < now
            and now < self.applications_close + GRACE_PERIOD
        )

    def registration_available(self):
        """
        Returns True if trippee registration is available
        """
        now = timezone.now()
        return (
            self.trippee_registrations_open < now
            and now < self.trippee_registrations_close
        )

    def reset(self):
        """
        Hide all statuses.
        """
        self.scoring_available = False
        self.hide_volunteer_page = False
        self.application_status_available = False
        self.leader_assignment_available = False
        self.trippee_assignment_available = False

        self.save()
