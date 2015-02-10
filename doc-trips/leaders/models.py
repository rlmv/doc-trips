

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models import ManyToManyField, CharField, ForeignKey, TextField, BooleanField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from db.models import DatabaseModel
from leaders.managers import LeaderApplicationManager
from trips.models import Section, TripType, ScheduledTrip

# TODO: move to globals and reuse for trippees
TSHIRT_SIZE_CHOICES = (
    ('S', 'Small'), 
    ('M', 'Medium'), 
    ('L', 'Large'), 
    ('XL', 'Extra large'),
)

class LeaderApplicationQuestion(DatabaseModel):
    
    class Meta:
        ordering = ['ordering']
        
    question = models.TextField()
    ordering = models.IntegerField()

class LeaderApplicationAnswer(DatabaseModel):

    class Meta:
        ordering = ['question__ordering']

    answer = models.TextField(blank=True)
    question = models.ForeignKey(LeaderApplicationQuestion)
    application = models.ForeignKey('LeaderApplication', 
                                    related_name='answers', 
                                    editable=False)


class LeaderApplication(DatabaseModel):

    objects = LeaderApplicationManager()
    
    """ Status choices. 

    See https://docs.djangoproject.com/en/dev/ref/models/fields/#choices
    """
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    WAITLISTED = 'WAITLISTED'
    REJECTED = 'REJECTED'
    CROO = 'CROO'
    CANCELED = 'CANCELED'
    DEPRECATED = 'DEPRECATED'
    DISQUALIFIED = 'DISQUALIFIED'
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

    # ---- administrative information. not seen by applicants ------
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=PENDING, 
                              verbose_name="Application status")
    assigned_trip = models.ForeignKey(ScheduledTrip, null=True, 
                                      blank=True, related_name='leaders',
                                      on_delete=models.SET_NULL)

    # ----- trainings -----
    community_building = models.DateField(null=True, blank=True)
    risk_management = models.DateField(null=True, blank=True)
    wilderness_skills = models.DateField(null=True, blank=True)
    first_aid = models.DateField('First Aid/CPR', null=True, blank=True)

    
    # ----- general information, not shown to graders ------
    class_year = models.PositiveIntegerField()
    gender = models.CharField(max_length=25)
    hinman_box = models.CharField(max_length=10)
    phone = models.CharField('Phone Number', max_length=255)
    from_where = CharField(max_length=255, verbose_name='Where are you from?')
    what_do_you_like_to_study = CharField(max_length=255, verbose_name='What do you like to study?')
    tshirt_size = models.CharField(max_length=2, choices=TSHIRT_SIZE_CHOICES)

    dietary_restrictions = TextField(blank=True, verbose_name="Do you have any dietary restrictions or allergies that we should know about?")
    allergen_information = TextField(blank=True, verbose_name="What happens if you come into contact with this allergen (e.g. I turn purple and squishy if I eat a grape!)?")

    trippee_confidentiality = BooleanField(default=False, verbose_name="If selected to be a DOC Trips Leader, I understand that I will be given access to my Trippees' confidential medical information for safety purposes. I pledge to maintain the confidentiality of this information, except as is required by medical or legal concerns")
    in_goodstanding_with_college = BooleanField(default=False, verbose_name="By applying to lead a DOC Trip, I acknowledge that I am in good standing with the College. This may be verified by DOC Trips through the Undergraduate Dean’s Office.")

    #  ------  trip and section information ------
    preferred_sections = ManyToManyField(Section, blank=True,
                                         related_name='preferred_leaders')
    available_sections = ManyToManyField(Section, blank=True,
                                         related_name='available_leaders')
    preferred_triptypes = ManyToManyField(TripType, blank=True,
                                          related_name='preferred_leaders',
                                         verbose_name='Preferred types of trips')
    available_triptypes = ManyToManyField(TripType, blank=True, 
                                          related_name='available_triptypes', 
                                          verbose_name='Available types of trips')

    trip_preference_comments = TextField(blank=True, verbose_name="Looking at the Trips descriptions, please feel free to use this space to address any concerns or explain your availability. This will only be used to help us in Trip assignments, it will not be considered when your application is being read.")

    cannot_participate_in = TextField(blank=True, verbose_name="If applicable, please elaborate (to the extent you feel comfortable) on any particular trips or activities that you absolutely cannot participate in. This information will be used exclusively for trip assignments & co-leader pairings. All information in this application will remain confidential.")

    personal_activities = TextField(blank=True, verbose_name='Please list your primary activities and involvements at Dartmouth and beyond')

    went_on_trip = BooleanField(default=False, verbose_name='Did you go on a First Year Trip?')
    applied_to_trips = BooleanField(default=False, verbose_name='Have you applied to lead a Trip before?')
    in_hanover_this_fall = BooleanField(default=False, verbose_name='Are you planning to be in Hanover this fall?')
    
    spring_leader_training_ok = BooleanField(default=False, verbose_name="I can attend Leader Training during the spring term.")

    summer_leader_training_ok = BooleanField(default=False, verbose_name="I can attend Leader Training during the summer term.")

    def clean(self):
        """ Make sure that leaders can only be assigned to trips if status==ACCEPTED.
        
        This is called by django to validate ModelForms and the like.
        """
        if self.status != self.ACCEPTED and self.assigned_trip:
            raise ValidationError("A '{}' LeaderApplication cannot be assigned to a trip. "
                                  "Change status to 'Accepted' or remove trip assignment.".format(self.get_status_display()))

    def __str__(self):
        return str(self.applicant)


    def get_preferred_trips(self):
        """ All scheduled trips which this leader prefers to go lead. """

        trips = (ScheduledTrip.objects
                 .filter(trips_year=self.trips_year)
                 .filter(Q(section__in=self.preferred_sections.all()) &
                         Q(template__triptype__in=self.preferred_triptypes.all())))

        return trips


    def get_available_trips(self):
        """
        Return all ScheduledTrips which this leader is available for. 
        
        Contains all permutations of available and preferred sections and 
        trips types, excluding the results of get_preferred_trips.
        """
        
        trips = (ScheduledTrip.objects
                 .filter(trips_year=self.trips_year)
                 .filter(Q(section__in=self.preferred_sections.all()) |
                         Q(section__in=self.available_sections.all()), 
                         Q(template__triptype__in=self.preferred_triptypes.all()) |
                         Q(template__triptype__in=self.available_triptypes.all()))
                 .exclude(id__in=self.get_preferred_trips().all()))

        return trips
                 

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

    
    
    
