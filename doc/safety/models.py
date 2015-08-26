from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse

from doc.db.models import DatabaseModel
from doc.trips.models import Trip
from doc.utils.model_fields import YesNoField

"""
Models for Incident Reports
"""

ROLE_CHOICES = (
    ('TRIP_LEADER', 'Trip Leader'),
    ('CROO_MEMBER', 'Croo Member'),
    ('TRIPPEE', 'Trippee'),
    ('OTHER', 'Other')
)

class _IncidentBase(DatabaseModel):
    """ 
    Base fields for Incident and IncidentUpdate
    """
    class Meta:
        abstract = True

    # inputing user
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    caller = models.CharField("Who called?", max_length=255)
    caller_role = models.CharField(choices=ROLE_CHOICES, max_length=20)
    # TODO fill in other
    caller_number = models.CharField(max_length=20)  # phone number


class Incident(_IncidentBase):

    class Meta:
        ordering = ['-when']

    trip = models.ForeignKey(
        Trip, blank=True, null=True,
        verbose_name='On what trip did this incident occur?',
        help_text='leave blank if incident did not occur on a trip'
    )
    where = models.TextField(
        "Where during the trip did this occur?",
        help_text="trail name, campsite, Hanover, Lodge, etc"
    )
    when = models.DateTimeField("When did this incident occur?")

    injuries = YesNoField('Did any injuries take place during this incident?')
    subject = models.CharField("Who did this happen to?", blank=True, max_length=255)
    subject_role = models.CharField(choices=ROLE_CHOICES, blank=True, max_length=20)
    # TODO fill in other

    desc = models.TextField('Describe the incident')
    resp = models.TextField('What was the response to the incident?')
    outcome = models.TextField('What was the outcome of the response?')
  
    follow_up = models.TextField(
        'Is any additional follow-up needed? If so, what?'
    )

    # TODO: closed? resolved?
    
    def detail_url(self):
        return reverse('db:safety:detail', kwargs=self.obj_kwargs())

    def __str__(self):
        fmt = lambda x: x.strftime("%m/%d %X")
        if self.trip:
            return "%s: %s" % (fmt(self.when), self.trip)
        return fmt(self.when)


class IncidentUpdate(_IncidentBase):
    incident = models.ForeignKey(Incident, editable=False)  # parent
    update = models.TextField()

    class Meta:
        ordering = ['created']
