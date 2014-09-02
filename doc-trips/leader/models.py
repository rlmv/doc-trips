

from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from db.models import DatabaseModel
from leader.managers import LeaderApplicationManager

# TODO: move to globals and reuse for trippees
TSHIRT_SIZE_CHOICES = (
    ('S', 'Small'), 
    ('M', 'Medium'), 
    ('L', 'Large'), 
    ('XL', 'Extra large'),
)


class LeaderApplication(DatabaseModel):

    objects = LeaderApplicationManager()
    
    """ Status choices. 

    See https://docs.djangoproject.com/en/dev/ref/models/fields/#choices
    """
    PENDING = 'PEND'
    ACCEPTED = 'ACC'
    WAITLISTED = 'WAIT'
    REJECTED = 'REJ'
    CROO = 'CROO'
    CANCELED = 'CANC'
    DEPRECATED = 'DEP'
    DISQUALIFIED = 'DISQ'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (WAITLISTED, 'Waitlisted'), 
        (REJECTED, 'Rejected'), 
        (CROO, 'Croo'),
        (CANCELED, 'Cancelled'),
        (DEPRECATED, 'Deprecated'),
        (DISQUALIFIED, 'Disqualified'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    assigned_trip = models.ForeignKey('trip.ScheduledTrip', null=True, blank=True, related_name='leaders')

    status = models.CharField(max_length=4, choices=STATUS_CHOICES, default=PENDING)
    class_year = models.PositiveIntegerField()
    tshirt_size = models.CharField(max_length=2, choices=TSHIRT_SIZE_CHOICES)
    gender = models.CharField(max_length=255)
    hinman_box = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    offcampus_address = models.CharField(max_length=255, blank=True)     # TODO: do we need this?

    # reverse lookups from Section are not needed, hence the '+'
    # leaders for a section can be looked up via assigned_trip.section.
    # (We may later need this to suggest leaders to assign to a trip.)
    preferred_sections = models.ManyToManyField('trip.Section', related_name='+', blank=True)
    available_sections = models.ManyToManyField('trip.Section', related_name='+', blank=True)

    # TODO: should application questiosn and answers be hardcoded or dynamic?

    notes = models.CharField(max_length=255, blank=True) # not required in form

    def clean(self):
        """ Make sure that leaders can only be assigned to trips if status==ACCEPTED.
        
        This is called by django to validate ModelForms and the like. See
        https://docs.djangoproject.com/en/dev/ref/models/instances/#django.db.models.Model.clean
        """
        if self.status != self.ACCEPTED and self.assigned_trip:
            raise ValidationError("A '{}' LeaderApplication cannot be assigned to a trip. "
                                  "Change status to 'Accepted' or remove trip assignment.".format(self.get_status_display()))

    def __str__(self):
        return self.user.username
        

def validate_grade(grade):
    min = LeaderGrade.MIN_GRADE
    max = LeaderGrade.MAX_GRADE
    if grade < min or grade > max:
        raise ValidationError('grade is not in required range [{}, {}]'
                              .format(min, max))


class LeaderGrade(DatabaseModel):

    MIN_GRADE = 0
    MAX_GRADE = 5

    grader = models.ForeignKey(settings.AUTH_USER_MODEL)
    leader_application = models.ForeignKey(LeaderApplication, related_name='grades')
    grade = models.DecimalField(max_digits=3, decimal_places=1, 
                                validators=[ validate_grade ])
    comment = models.CharField(max_length=255)
    hard_skills = models.BooleanField(default=False)
    soft_skills = models.BooleanField(default=False)

    
    
    
