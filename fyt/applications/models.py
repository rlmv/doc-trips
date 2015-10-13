
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from .managers import (CrooApplicationManager, LeaderApplicationManager,
                       GeneralApplicationManager)
from fyt.db.models import DatabaseModel
from fyt.croos.models import Croo
from fyt.trips.models import Trip, Section, TripType
from fyt.utils.choices import YES_NO_CHOICES, TSHIRT_SIZE_CHOICES
from fyt.utils.models import MedicalMixin

"""
Models for Leaders and Croo applications
"""


class ApplicationInformation(DatabaseModel):
    """
    Model for croo and leader application information.
    """
    class Meta:
        unique_together = ['trips_year']

    leader_supplement_questions = models.FileField(
        'Leader Application questions', help_text='.docx file')
    croo_supplement_questions = models.FileField(
        'Croo Application questions', help_text='.docx file')

    application_header = models.TextField(
        blank=True, help_text=(
            "This will be displayed at the top of all application pages"
        )
    )
    general_info = models.TextField(
        blank=True, help_text=(
            "This will be displayed at the top of the General Information tab"
        )
    )
    leader_info = models.TextField(
        blank=True, help_text=(
            "This will be displayed at the top of the Leader Application tab"
        )
    )
    croo_info = models.TextField(
        blank=True, help_text=(
            "This will be displayed at the top of Croo Application tab"
        )
    )


class PortalContent(DatabaseModel):
    """
    Content to display to users in the volunteer portal
    """
    class Meta:
        unique_together = ['trips_year']

    PENDING_description = models.TextField(blank=True)
    CROO_description = models.TextField(blank=True)
    LEADER_description = models.TextField(blank=True)
    LEADER_WAITLIST_description = models.TextField(blank=True)
    REJECTED_description = models.TextField(blank=True)
    CANCELED_description = models.TextField(blank=True)
   
    day0_description = models.TextField(
        'day 0 description', blank=True, help_text=(
            "description for leaders' first day, Gilman Island, etc."
        )
    )
    day1_description = models.TextField(
        'day 1 description', blank=True, help_text=(
            "post-Gilman, trippee arrival, swim test, safety talk, etc."
        )
    )
    day5_description = models.TextField(
        'day 5 description', blank=True, help_text="return to campust, pre-o"
    )

    def get_status_description(self, status):
        """
        Given a GeneralApplication.status choice, return the description
        """
        return {
            GeneralApplication.PENDING: self.PENDING_description,
            GeneralApplication.CROO: self.CROO_description,
            GeneralApplication.LEADER: self.LEADER_description,
            GeneralApplication.LEADER_WAITLIST: self.LEADER_WAITLIST_description,
            GeneralApplication.REJECTED: self.REJECTED_description,
            GeneralApplication.CANCELED: self.CANCELED_description
        }[status]


def validate_condition_true(value):
    if value is not True:
        raise ValidationError('You must agree to this condition')


class GeneralApplication(MedicalMixin, DatabaseModel):
    """
    Contains shared information for Croo and Leader applications.

    TODO: rename to Application? Volunteer? mv questionaire to separate model?
    """
    class Meta:
        ordering = ['applicant']

    objects = GeneralApplicationManager()

    PENDING = 'PENDING'
    CROO = 'CROO'
    LEADER = 'LEADER'
    LEADER_WAITLIST = 'LEADER_WAITLIST'
    REJECTED = 'REJECTED'
    CANCELED = 'CANCELED'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (CROO, 'Croo'),
        (LEADER, 'Leader'),
        (LEADER_WAITLIST, 'Leader Waitlist'),
        (REJECTED, 'Rejected'),
        (CANCELED, 'Canceled'),
    )

    # ---- administrative information. not seen by applicants ------
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, editable=False, related_name='applications'
    )
    status = models.CharField(
        "Application status", max_length=15, choices=STATUS_CHOICES, default=PENDING
    )
    assigned_trip = models.ForeignKey(
        Trip, blank=True, null=True,
        related_name='leaders', on_delete=models.PROTECT
    )
    assigned_croo = models.ForeignKey(
        Croo, blank=True, null=True,
        related_name='croo_members', on_delete=models.PROTECT
    )
    safety_lead = models.BooleanField(default=False)  # TODO: remove?

    # ----- trainings -----

    community_building = models.DateField(null=True, blank=True)
    risk_management = models.DateField(null=True, blank=True)
    wilderness_skills = models.DateField(null=True, blank=True)
    croo_training = models.DateField(null=True, blank=True)
    OTHER = 'other'
    FIRST_AID_CHOICES = (
        (None, '--'),
        ('FA', 'First Aid'),
        ('CPR', 'CPR'),
        ('FA/CPR', 'First Aid/CPR'),
        ('WFA', 'WFA'),
        ('WFR', 'WFR'),
        ('W-EMT', 'W-EMT'),
        ('EMT', 'EMT'),
        ('OEC', 'OEC'),
        (OTHER, 'other'),
    )
    # first aid certs - filled in by directors
    fa_cert = models.CharField(
        'first aid cert', max_length=10, blank=True, default="",
        choices=FIRST_AID_CHOICES
    )
    fa_other = models.CharField(
        'other first aid cert', max_length=100, blank=True, default=""
    )

    def get_first_aid_cert(self):
        """
        Get the applicants first aid cert; choice or other
        """
        if self.fa_cert == self.OTHER or not self.fa_cert:
            return self.fa_other
        return self.fa_cert

    # ----- general information, not shown to graders ------

    class_year = models.PositiveIntegerField()
    gender = models.CharField(max_length=25)
    race_ethnicity = models.CharField(
        'race/ethnicity', max_length=255, blank=True, help_text='optional'
    )
    hinman_box = models.CharField(max_length=10)
    phone = models.CharField('cell phone number', blank=True, max_length=255)
    summer_address = models.CharField(
        blank=True, max_length=255, help_text="don't worry if you don't know yet"
    )
    tshirt_size = models.CharField(max_length=2, choices=TSHIRT_SIZE_CHOICES)

    from_where = models.CharField('Where are you from?', max_length=255)
    what_do_you_like_to_study = models.CharField(
        'What do you like to study?', max_length=255
    )
    personal_activities = models.TextField(
        "In order of importance to you, please list your activities "
        "and involvements at Dartmouth and beyond (e.g. greek "
        "affiliation, affinity group, campus organization, team, etc)",
        blank=True
    )
    feedback = models.TextField(
        "If you have any experience with Trips, what would you "
        "change about the program (big or small)?  If you do not "
        "have experience with Trips, what would you change about "
        "the program OR what would you change about your introduction "
        "to Dartmouth?",
        blank=True
    )
    hanover_in_fall = models.CharField(
        'Are you planning to be in Hanover this fall?',
        choices=YES_NO_CHOICES, max_length=5
    )
    LEADER_CROO_PREFERENCE = (
        ('PREFER_LEADER', 'Prefer Trip Leader'),
        ('PREFER_CROO', 'Prefer Croo'),
        ('N/A', 'N/A'),
    )
    role_preference = models.CharField(
        "While Trips Directorate will ultimately decide where we think "
        "you will be most successful in the program, we would like to "
        "know your preferences. If you are submitting a Trip Leader "
        "application AND a Croo application, please indicate which "
        "position you prefer. If you are only applying to one position, "
        "please choose 'N/A'",
        choices=LEADER_CROO_PREFERENCE, default='N/A', max_length=20
    )
  
    # ------ certs -------
    medical_certifications = models.TextField(
        "Current trainings in First Aid and CPR are required for all DOC "
        "trip leaders and croo members. Please list any relevant medical "
        "certifications you hold (e.g. First Aid, CPR, Wilderness First Aid, "
        "Wilderness First Responder, Emergency Medical Technician, Wilderness "
        "Emergency Medical Technician, Outdoor Emergency Care). Also list the "
        "program that sponsored the certification, and the dates they expire. "
        "If you do not currently have such a certification (or if your "
        "certification will expire before Trips ends), we will be in touch "
        "about how you can get trained through Trips-sponsored First Aid & "
        "CPR courses in the spring and summer.",
        blank=True, help_text=(
            "eg. 'First Aid - American Red Cross, expires October 2013.'"
        )
    )
    medical_experience = models.TextField(
        "Briefly describe your experience with your safety certifications. "
        "How frequently do you use your certification and in what circumstances?",
        blank=True
    )
    peer_training = models.TextField(
        "List and briefly describe any peer training program "
        "(DPP, IGD, DBI, MAV, EDPA, SAPA, DAPA, UGA, etc.) that you "
        "have lead or participated in.",
        blank=True
    )

    # ------- notices -------
    trippee_confidentiality = models.BooleanField(
        "If selected to be a Trips Leader or a Croo member, I understand "
        "that I will be given access to Trippees' confidential medical "
        "information for safety purposes. I pledge to maintain the "
        "confidentiality of this information, except as is required by "
        "medical or legal concerns",
        default=False, validators=[validate_condition_true]
    )
    in_goodstanding_with_college = models.BooleanField(
        "By applying to lead a DOC Trip, I acknowledge that I am in good "
        "standing with the College. This may be verified by DOC Trips "
        "through the Undergraduate Dean’s Office.",
        default=False, validators=[validate_condition_true]
    )
    trainings = models.BooleanField(
        "I understand that if I am accepted as a Crooling or Trip Leader "
        "I will be required to get First Aid and CPR training, as well as "
        "attend croo and leader specific training. I understand that if I "
        "do not meet these requirements, I will not be able to be on a "
        "Croo/lead a trip.",
        default=False, validators=[validate_condition_true]
    )
    spring_training_ok = models.BooleanField(
        "I can attend trainings during the spring term.", default=False
    )
    summer_training_ok = models.BooleanField(
        "I can attend trainings during the summer term.", default=False
    )

    def clean(self):
        """
        Only allow Croo/Trip assignments if status == LEADER,CROO 
        """
        if self.assigned_trip and self.status != self.LEADER:
            msg = ("Volunteer %s with status %s cannot also lead a trip. "
                   "Change status to %s or remove Trip assignment")
            raise ValidationError(msg % (self, self.status, self.LEADER))

        if self.assigned_croo and self.status != self.CROO:
            msg = ("Volunteer %s with status %s cannot also be on a Croo. "
                   "Change status to %s or remove Croo assignment")
            raise ValidationError(msg % (self, self.status, self.CROO))

    @property
    def name(self):
        return self.applicant.name

    @property
    def lastname(self):
        return self.name.split()[-1]

    def leader_application_complete(self):
        """
        Leader application is complete if supplement is uploaded
        """
        return (hasattr(self, 'leader_supplement') and
                self.leader_supplement.document)

    def croo_application_complete(self):
        """
        Croo application is complete if supplement is uploaded
        """
        return (hasattr(self, 'croo_supplement') and
                self.croo_supplement.document)

    def get_preferred_trips(self):
        return self.leader_supplement.get_preferred_trips()

    def get_available_trips(self):
        return self.leader_supplement.get_available_trips()

    def detail_url(self):
        return reverse('db:generalapplication_detail', kwargs=self.obj_kwargs())

    def __str__(self):
        return self.name


class LeaderSupplement(DatabaseModel):
    """
    Leader application answers
    """
    NUMBER_OF_GRADES = 4

    objects = LeaderApplicationManager()

    application = models.OneToOneField(
        GeneralApplication, editable=False, related_name='leader_supplement'
    )
    document = models.FileField(
        'leader application answers', blank=True, db_index=True
    )

    #  ------  trip and section availability ------
    preferred_sections = models.ManyToManyField(
        Section, blank=True, related_name='preferred_leaders'
    )
    available_sections = models.ManyToManyField(
        Section, blank=True, related_name='available_leaders'
    )
    preferred_triptypes = models.ManyToManyField(
        TripType, blank=True, related_name='preferred_leaders',
        verbose_name='Preferred types of trips'
    )
    available_triptypes = models.ManyToManyField(
        TripType, blank=True, related_name='available_triptypes',
        verbose_name='Available types of trips'
    )

    # ------- availibilty and experience --------
    trip_preference_comments = models.TextField(
        "Looking at the Trips descriptions, please feel free to use "
        "this space to address any concerns or explain your availability. "
        "This will only be used to help us in Trip assignments, it will "
        "not be considered when your application is being read.",
        blank=True
    )
    cannot_participate_in = models.TextField(
        "If applicable, please elaborate (to the extent you feel comfortable) "
        "on any particular trips or activities that you absolutely cannot "
        "participate in. This information will be used exclusively for trip "
        "assignments & co-leader pairings. All information in this application "
        "will remain confidential.",
        blank=True
    )
    relevant_experience = models.TextField(
        "For each type of trip you are interested in leading, please describe "
        "your level of expertise and any amount of previous experience that "
        "might qualify you to lead that particular trip (DOC Wilderness "
        "Leader, lifeguard training, yoga experience, mountain biking "
        "enthusiast, photography class, NOLS, etc.).",
        blank=True
    )
        
    def get_preferred_trips(self):
        """
        All trips which this applicant prefers to lead
        """
        return (
            Trip.objects
            .filter(trips_year=self.trips_year)
            .filter(Q(section__in=self.preferred_sections.all()) &
                    Q(template__triptype__in=self.preferred_triptypes.all()))
        )

    def get_available_trips(self):
        """
        Return all Trips which this leader is available to lead.
        
        Contains all permutations of available and preferred sections and
        trips types, excluding the results of ``get_preferred_trips``.
        """
        return (
            Trip.objects
            .filter(trips_year=self.trips_year)
            .filter(Q(section__in=self.preferred_sections.all()) |
                    Q(section__in=self.available_sections.all()),
                    Q(template__triptype__in=self.preferred_triptypes.all()) |
                    Q(template__triptype__in=self.available_triptypes.all()))
            .exclude(id__in=self.get_preferred_trips().all())
        )

    def average_grade(self):
        """ 
        Average grade for the leader application.
        """
        r = self.grades.all().aggregate(models.Avg('grade'))
        return r['grade__avg']

    def get_absolute_url(self):
        return self.application.get_absolute_url()

    def __str__(self):
        return str(self.application)


class CrooSupplement(DatabaseModel):
    """
    Croo application answers
    """
    NUMBER_OF_GRADES = 4
    objects = CrooApplicationManager()

    application = models.OneToOneField(
        GeneralApplication, editable=False, related_name='croo_supplement'
    )
    document = models.FileField('Croo Application Answers', blank=True)

    # --- croo positions ------
    safety_lead_willing = models.BooleanField(
        'Yes, I am willing to be a Safety Lead', default=False
    )
    kitchen_lead_willing = models.BooleanField(
        'Yes, I am willing to be a Kitchen Witch/Wizard', default=False
    )
    kitchen_lead_qualifications = models.TextField(
        "If you are willing to be a Kitchen Witch/Wizard, please briefly "
        "describe your qualifications for the position", help_text=(
            "(eg. on Moosilauke Lodge crew spring 2014, experience "
            "working in industrial kitchens, experience preparing and "
            "organizing food for large groups)"
        ), blank=True
    )
   
    # -------- driving -------
    # TODO: mv from document

    def average_grade(self):
        """ Average grade for the croo application """
        r = self.grades.all().aggregate(models.Avg('grade'))
        return r['grade__avg']

    def get_absolute_url(self):
        return self.application.get_absolute_url()

    def __str__(self):
        return str(self.application)


class AbstractGrade(DatabaseModel):
    """
    Abstract model for shared grade information

    Concrete grade objects must implement an 'application' field
    """
    class Meta:
        abstract = True

    SCORE_CHOICES = (
        (1, "1 -- Bad application -- I really don't want this person to be a volunteer and I have serious concerns"),
        (2, "2 -- Poor application -- I have some concerns about this person being a Trips volunteer"),
        (3, "3 -- Fine application -- This person might work well as a volunteer but I have some questions"),
        (4, "4 -- Good application -- I would consider this person to be a volunteer but I wouldn't be heartbroken if they were not selected"),
        (5, "5 -- Great application -- I think this person would be a fantastic volunteer"),
        (6, "6 -- Incredible application -- I think this person should be one of the first to be selected to be a volunteer. I would be very frustrated/angry if this person is not selected"),
    )
    
    # related_name will be leaderapplicationgrades or crooapplicationgrades. Sweet.
    grader = models.ForeignKey(
        settings.AUTH_USER_MODEL, editable=False, related_name='%(class)ss'
    )
    grade = models.PositiveSmallIntegerField('score', choices=SCORE_CHOICES)
    hard_skills = models.CharField(max_length=255, blank=True)
    soft_skills = models.CharField(max_length=255, blank=True)
    comment = models.TextField()

    def __str__(self):
        return "%s's grade for %s" % (self.grader, self.application)


class LeaderApplicationGrade(AbstractGrade):
    """ Grade for LeaderApplications """
    application = models.ForeignKey(
        LeaderSupplement, related_name='grades', editable=False
    )


class CrooApplicationGrade(AbstractGrade):
    """ 
    Grade for CrooApplications
    """
    application = models.ForeignKey(
        CrooSupplement, related_name='grades', editable=False
    )
    qualifications = models.ManyToManyField('QualificationTag', blank=True)


class QualificationTag(DatabaseModel):
    """
    Used to mark Croo apps with hard skills relevant to different Croos 

    TODO: do we need views for adding/editing more tags?
    Or just a management command?
    """
    name = models.CharField(
        "I think this applicant is qualified for the following roles:",
        max_length=30
    )
   
    def __str__(self):
        return self.name


class AbstractSkippedGrade(DatabaseModel):
    """
    Abstract model to mark an application as skipped by a grader 

    If a grader skips an application they will not be shown the
    application again.
    """
    grader = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)

    class Meta:
        abstract = True


class SkippedLeaderGrade(AbstractSkippedGrade):
    """
    Skipped leader application
    """
    application = models.ForeignKey(
        LeaderSupplement, editable=False, related_name='skips'
    )


class SkippedCrooGrade(AbstractSkippedGrade):
    """
    Skipped croo application
    """
    application = models.ForeignKey(
        CrooSupplement, editable=False, related_name='skips'
    )
    # marks whether the grader was grading for a particular
    # qualification when they skipped the application
    for_qualification = models.ForeignKey(
        QualificationTag, null=True, editable=False
    )
