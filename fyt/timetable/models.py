
from datetime import timedelta

from django.utils import timezone
from django.db import models

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
        timetable, created = self.get_or_create(id=TIMETABLE_ID)
        return timetable


class Timetable(models.Model):
    """
    Singleton model for important dates
    """
    applications_open = models.DateTimeField(default=timezone.now)
    applications_close = models.DateTimeField(default=timezone.now)

    hide_volunteer_page = models.BooleanField(
        default=False, help_text=(
            "Enabling this will hide the database Volunteers page from "
            "everyone except directors and trip leader trainers. Use "
            "this during grading to prevent graders from seeing "
            "applicant's scores."
        )
    )
    application_status_available = models.BooleanField(
        default=False, help_text=(
            "Turn this on once all decisions have been made "
            "regarding Leaders and Croos"
        )
    )
    leader_assignment_available = models.BooleanField(
        default=False, help_text=(
            "Turn this on to let Trip Leaders see information "
            "about their assigned trip"
        )
    )
    trippee_registrations_open = models.DateTimeField(default=timezone.now)
    trippee_registrations_close = models.DateTimeField(default=timezone.now)
    trippee_assignment_available = models.BooleanField(
        default=False, help_text=(
            "Turn this on to let Incoming Students see their trip assignments"
        )
    )

    objects = TimetableManager()

    def save(self, *args, **kwargs):
        self.id = TIMETABLE_ID
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    def applications_available(self):
        """
        Are Croo and Leader applications available?

        Users can still submit an application 15 minutes after the posted
        deadline. This keeps people from losing data when they try and submit
        at the very last minute.
        """
        now = timezone.now()
        return (self.applications_open < now and
                now < self.applications_close + GRACE_PERIOD)

    def grading_available(self):
        """
        Is it before the application deadling?
        """
        return self.applications_close < timezone.now()

    def registration_available(self):
        """
        Returns True if trippee registration is available
        """
        now = timezone.now()
        return (self.trippee_registrations_open < now and
                now < self.trippee_registrations_close)
