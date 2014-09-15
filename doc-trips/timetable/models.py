

from django.utils import timezone
from django.db import models

TIMETABLE_ID = 1

class TimetableManager(models.Manager):

    def timetable(self):
        
        timetable, created = self.get_or_create(id=TIMETABLE_ID)
        return timetable


class Timetable(models.Model):
    """ 
    Singleton model for important dates
    """
    leader_application_open = models.DateTimeField(default=timezone.now)
    leader_application_closed = models.DateTimeField(default=timezone.now)

    # TODO: ??? are we going to have leader recs?
    # leader_recommendation_due = models.DateTimeField()

    leader_assignment_posted = models.DateTimeField(default=timezone.now)
    trippee_registration_open = models.DateTimeField(default=timezone.now)
    trippee_registration_closed = models.DateTimeField(default=timezone.now)
    trippee_assignment_posted = models.DateTimeField(default=timezone.now)

    migration_date = models.DateTimeField(default=timezone.now)

    objects = TimetableManager()

    def save(self, *args, **kwargs):
        self.id = TIMETABLE_ID
        super(Timetable, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    def is_leader_application_available(self):

        now = timezone.now()
        return (self.leader_application_open < now and
                now < self.leader_application_closed)
        
