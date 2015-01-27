

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

    # ---- administrative information. not seen by applicants ------
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Applicant")
    status = models.CharField(max_length=4, choices=STATUS_CHOICES, default=PENDING, 
                              verbose_name="Application status")
    assigned_trip = models.ForeignKey(ScheduledTrip, null=True, 
                                      blank=True, related_name='leaders',
                                      on_delete=models.SET_NULL)
    
    # ----- general information, not shown to graders ------
    class_year = models.PositiveIntegerField()
    gender = models.CharField(max_length=25)
    hinman_box = models.CharField(max_length=10)
    phone = models.CharField(max_length=255, verbose_name='Phone number')
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

    
    # ---- application questions -----

    personal_activities = TextField(blank=True, verbose_name='Please list your primary activities and involvements at Dartmouth and beyond')
    personal_communities = TextField(blank=True, verbose_name="Are there any communities with which you identify? You are welcome to list more than one, or leave this blank. Be as brief or detailed as you’d like.")
    
    went_on_trip = BooleanField(default=False, verbose_name='Did you go on a First Year Trip?')
    applied_to_trips = BooleanField(default=False, verbose_name='Have you applied to lead a Trip before?')
    is_in_hanover_this_fall = BooleanField(default=False, verbose_name='Are you planning to be in Hanover this fall?')
    
    tell_us_about_yourself = TextField(blank=True, verbose_name="Without simply listing activities, tell us about yourself. What are you passionate about? What identities are meaningful to you? Feel free to answer this question in the way most comfortable for you.")

    comforting_experience = TextField(blank=True, verbose_name="Describe an experience in which someone else (a friend, roommate, classmate, etc.) felt uncomfortable. What did you do to make them feel more comfortable and welcome in that environment?")

    best_compliment = TextField(blank=True, verbose_name="What is the best compliment (serious, funny, reflective, goofy, etc.) you have ever received (or wish you had received)?")

    trip_leader_roles = TextField(blank=True, verbose_name="What role do trip leaders play in the broader purpose(s) of DOC Trips? How will you, as a trip leader, further these goals both during your trip as well as back on campus?")

    what_to_change_about_trips = TextField(blank=True, verbose_name="If you have led a DOC Trip before, what would you change about the program (big or small)? If you have not led a DOC Trip before, what would you change about the program (big or small) OR what would you change about your introduction to Dartmouth?")

    leadership_experience = TextField(blank=True, verbose_name="Describe a leadership experience you had (in high school, at Dartmouth, as a former trip leader, etc.). What specific skills and insights did you bring to that experience? How would you describe yourself as a leader?")

    working_with_difference = TextField(blank=True, verbose_name="Discuss a situation (in high school, at Dartmouth, on an off-term, etc.) in which you had to work with someone who was very different from yourself. How did you respond to these differences?")

    coleader_qualities = TextField(blank=True, verbose_name="Trip leaders work closely with their co-leader before, during, and after the trip. What qualities would you value in a co-leader that both balance your weaknesses AND complement your strengths?")

    why_do_you_want_to_be_involved = TextField(blank=True, verbose_name="Why do you want to be involved in First-Year Trips as a trip leader?")

    medical_certifications = TextField(blank=True, verbose_name="Current certifications in Standard First Aid and CPR are required for all DOC trip leaders. Please list any relevant medical certifications you hold or have held, along with the program that sponsored the certification and the dates they expire — for example, 'First Aid (American Red Cross), expires October 2013'.")

    relevant_experience = TextField(blank=True, verbose_name="For each type of trip you are interested in leading, please describe your level of expertise and any amount of previous experience that might qualify you to lead that particular trip. Include any accomplishments, special skills, or certifications that you consider relevant (lifeguard training, yoga experience, mountain biking enthusiast, photography class, NOLS, skiing since you were a baby, etc.). No experience is completely fine! — our training will prepare you for just about anything you might encounter and you will be paired will a leader who complements your skill set.")

    cannot_participate_in = TextField(blank=True, verbose_name="If applicable, please elaborate (to the extent you feel comfortable) on any particular trips or activities that you absolutely cannot participate in. This information will be used exclusively for trip assignments & co-leader pairings. *NOTE: All information in this application will remain confidential.")

    spring_leader_training_ok = BooleanField(default=False, verbose_name="I can attend Leader Training during the spring term.")

    summer_leader_training_ok = BooleanField(default=False, verbose_name="I can attend Leader Training during the summer term.")

    express_yourself = TextField(blank=True, verbose_name="It’s always tough to say everything you want to in an application – so this is an opportunity to share any additional thoughts or information. If you’ve said enough, then feel free to leave this portion blank!")
    

    def clean(self):
        """ Make sure that leaders can only be assigned to trips if status==ACCEPTED.
        
        This is called by django to validate ModelForms and the like.
        """
        if self.status != self.ACCEPTED and self.assigned_trip:
            raise ValidationError("A '{}' LeaderApplication cannot be assigned to a trip. "
                                  "Change status to 'Accepted' or remove trip assignment.".format(self.get_status_display()))

    def __str__(self):
        return str(self.user)


    def get_preferred_trips(self):
        """ All scheduled trips which this leader prefers to go lead. """

        trips = (ScheduledTrip.objects
                 .filter(trips_year=self.trips_year)
                 .filter(Q(section__in=self.preferred_sections.all()) &
                         Q(template__trip_type__in=self.preferred_triptypes.all())))

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
                         Q(template__trip_type__in=self.preferred_triptypes.all()) |
                         Q(template__trip_type__in=self.available_triptypes.all()))
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

    
    
    
