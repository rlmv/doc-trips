
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from .managers import (
    CrooApplicationManager,
    GeneralApplicationManager,
    LeaderApplicationManager,
)

from fyt.croos.models import Croo
from fyt.db.models import DatabaseModel
from fyt.trips.models import Section, Trip, TripType
from fyt.utils.cache import cache_as
from fyt.utils.choices import (
    AVAILABLE,
    NOT_AVAILABLE,
    PREFER,
    TSHIRT_SIZE_CHOICES,
)
from fyt.utils.model_fields import NullYesNoField, YesNoField
from fyt.utils.models import MedicalMixin


"""
Models for Leaders and Croo applications

Note 1/28/2017: I refactored applications to use dynamic questions and answers.
Previously, applicants uploaded a .docx file with their answers in it, and
this determined whether the application was complete. With the new schema,
'completeness' is determined by whether the applicant answered all the
questions and indicated that they are willing to be a volunteer (leader or
croo.) These 'willing' fields were populated with historical data so that the
completeness of old applications did not change with this migration. All
queries should return the same results.
"""


class ApplicationInformation(DatabaseModel):
    """
    Model for croo and leader application information.
    """
    class Meta:
        unique_together = ['trips_year']

    application_questions = models.FileField(
        'Application questions', help_text='.docx file')

    application_header = models.TextField(
        blank=True, help_text=(
            "This will be displayed at the top of all application pages"
        )
    )

    # Deprecated questions from split croo/leader application
    # ----------------------------------------------------------

    _old_leader_supplement_questions = models.FileField(
        'Leader Application questions', help_text='.docx file')

    _old_croo_supplement_questions = models.FileField(
        'Croo Application questions', help_text='.docx file')

    _old_general_info = models.TextField(
        blank=True, help_text=(
            "This will be displayed at the top of the General Information tab"
        )
    )
    _old_leader_info = models.TextField(
        blank=True, help_text=(
            "This will be displayed at the top of the Leader Application tab"
        )
    )
    _old_croo_info = models.TextField(
        blank=True, help_text=(
            "This will be displayed at the top of Croo Application tab"
        )
    )


class Question(DatabaseModel):
    """
    An application question.
    """
    class Meta:
        ordering = ['index']

    index = models.PositiveIntegerField(
        'order', unique=True, help_text=(
            'change this value to re-order the questions'
        )
    )
    question = models.TextField(blank=False)

    def __str__(self):
        return "Question: {}".format(self.question)


class Answer(models.Model):
    """
    Through model for application answers.
    """
    class Meta:
        unique_together = ('application', 'question')
        ordering = ['question']

    application = models.ForeignKey(
        'GeneralApplication', on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE
    )
    answer = models.TextField(blank=True)

    def __str__(self):
        return "Answer: {}".format(self.answer)


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

    answers = models.ManyToManyField(Question, through=Answer)

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
        'Race/Ethnicity', max_length=255, blank=True
    )
    hinman_box = models.CharField(max_length=10)
    phone = models.CharField('cell phone number', blank=True, max_length=255)
    summer_address = models.CharField(
        blank=True, max_length=255, help_text=(
            'Tell us your home address if you are not yet sure of your summer '
            'address.'
        )
    )
    tshirt_size = models.CharField(max_length=3, choices=TSHIRT_SIZE_CHOICES)

    height = models.CharField(max_length=10, blank=True)
    weight = models.CharField(max_length=10, blank=True)

    gear = models.TextField(
        "Most trips require participants to have a frame pack, sleeping bag, "
        "and sleeping pad. What outdoor gear is available to you? Will you be "
        "able to borrow gear from friends and family or will you require "
        "rentals from DOC Trips?  While we will do our best to accommodate "
        "your gear needs if you are selected, priority will be given to "
        "first-years.",
        blank=True
    )

    from_where = models.CharField('Where are you from?', max_length=255)
    what_do_you_like_to_study = models.CharField(
        'What do you like to study?', max_length=255
    )
    personal_activities = models.TextField(
        "In order of importance to you, please list your activities, "
        "involvements, and communities at Dartmouth and beyond (e.g. greek "
        "affiliation, affinity group, campus organization, team, etc)",
        blank=True
    )
    feedback = models.TextField(
        "Based on your prior knowledge of and experience with Trips, do you "
        "have any suggestions to improve the program? If so, what? Remember "
        "that this question is ungraded and optional, but your feedback will "
        "help us improve the program for incoming students!",
        blank=True
    )
    hanover_in_fall = YesNoField(
        'Are you planning to be in Hanover this fall?'
    )

    transfer_exchange = YesNoField(
        'Are you a transfer or exchange student?'
    )

    LEADER_CROO_PREFERENCE = (
        ('PREFER_LEADER', 'Prefer Trip Leader'),
        ('PREFER_CROO', 'Prefer Crooling'),
        ('N/A', 'N/A'),
    )
    # TODO: rewrite this/connect to croo_willing/leader_willing
    role_preference = models.CharField(
        "While Trips Directorate will place you, we would like to "
        "know your preferences. If you are submitting a Trip Leader "
        "application AND a Crooling application, please indicate which "
        "position you prefer. If you are only applying to one position, "
        "please choose 'N/A'",
        choices=LEADER_CROO_PREFERENCE, default='N/A', max_length=20
    )

    leadership_style = models.TextField(
        'Describe your leadership style and your role in a group. Please go to '
        '<a href="https://sites.google.com/a/stgregoryschool.org/mr-roberts/home/theoretical-and-applied-leadership/leadership-squares">this website</a> '
        'and use the four descriptions (Puzzle Master, Director, Coach, or '
        'Diplomat) as a framework for your answer. Please order the four '
        'leadership styles in order of how much you identify with each one of '
        'them, and use them as a launching pad to discuss your strengths and '
        'weaknesses. This is not supposed to box you in to a specific '
        'category, but rather it serves to provide you with a structure to '
        'discuss your strengths and weaknesses and group-work styles so that '
        'we can effectively pair you with a co-leader or fellow croolings who '
        'complements you. Each leadership style is equally valuable, and we '
        'will use answers to this question to balance our teams as a whole.'
    )

    leader_willing = models.BooleanField(
        'I would like to be considered for a trip leader position. '
    )
    croo_willing = models.BooleanField(
        'I would like to be considered for a crooling position. (NOTE: ‘19s '
        'who are taking classes this sophomore summer can NOT apply, given '
        'the conflict of dates.)'
    )

    # ------ certs -------
    medical_certifications = models.TextField(
        "Please list any relevant medical "
        "certifications you hold (e.g. First Aid, CPR, Wilderness First Aid, "
        "Wilderness First Responder, Emergency Medical Technician, Wilderness "
        "Emergency Medical Technician, Outdoor Emergency Care). Also list the "
        "program that sponsored the certification, and the dates they expire.",
        blank=True, help_text=(
            "eg. 'First Aid - American Red Cross, expires October 2013.'"
        )
    )
    medical_experience = models.TextField(
        "Briefly describe your experience using your medical certifications. "
        "How frequently do you use your certifications and in what "
        "circumstances?",
        blank=True
    )
    peer_training = models.TextField(
        "List and briefly describe any peer training program "
        "(e.g. DPP, IGD, DBI, MAV, EDPA, SAPA, DAPA, UGA, etc.) that you "
        "have lead or participated in.",
        blank=True
    )

    # ------- notices -------
    trippee_confidentiality = models.BooleanField(
        "If selected to be a Trips volunteer, I understand "
        "that I will be given access to Trippees' confidential medical "
        "information for safety purposes. I pledge to maintain the "
        "confidentiality of this information, except as is required by "
        "medical or legal concerns",
        default=False, validators=[validate_condition_true]
    )
    in_goodstanding_with_college = models.BooleanField(
        "By applying to volunteer for Trips, I acknowledge that I am in good "
        "standing with the College. This will be verified by DOC Trips "
        "through the Undergraduate Dean’s Office.",
        default=False, validators=[validate_condition_true]
    )
    trainings = models.BooleanField(
        "I understand that if I am accepted as a Trips volunteer "
        "I will be required to get First Aid and CPR training, as well as "
        "attend croo- and leader-specific trainings. I understand that if I "
        "do not meet these requirements, I will not be able to volunteer for "
        "Trips.",
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

    def all_questions_answered(self):
        """
        Returns True if all the dynamic questions are answered.
        """
        q_ids = set(q.id for q in self.get_questions())

        for answer in self.answer_set.all():
            if answer.answer:  # "" is not an answer
                q_ids.remove(answer.question_id)

        return len(q_ids) == 0

    GET_QUESTIONS = '_get_questions'

    @cache_as(GET_QUESTIONS)
    def get_questions(self):
        """
        Used to cache this year's questions so that large querysets can be
        preloaded to improve efficiency.
        """
        return Question.objects.filter(trips_year=self.trips_year)

    @property
    def leader_application_complete(self):
        """
        A leader application is complete if all questions are answered
        and the applicant has indicated that they want to be a leader.
        """
        return self.leader_willing and self.all_questions_answered()

    @property
    def croo_application_complete(self):
        """
        A croo application is complete if all questions are answered
        and the applicant has indicated that they want to be on a croo.
        """
        return self.croo_willing and self.all_questions_answered()

    def answer_question(self, question, text):
        """
        Utility function to answer a question; mainly used for testing.
        """
        return Answer.objects.create(
            application=self,
            question=question,
            answer=text
        )

    def get_preferred_trips(self):
        return self.leader_supplement.get_preferred_trips()

    def get_available_trips(self):
        return self.leader_supplement.get_available_trips()

    def __str__(self):
        return self.name


LEADER_SECTION_CHOICES = (
    (PREFER, 'prefer'),
    (AVAILABLE, 'available'),
    (NOT_AVAILABLE, 'not available')
)

LEADER_TRIPTYPE_CHOICES = LEADER_SECTION_CHOICES


class LeaderSectionChoice(models.Model):

    class Meta:
        unique_together = ('application', 'section')

    application = models.ForeignKey(
        'LeaderSupplement', on_delete=models.CASCADE
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE
    )
    preference = models.CharField(
        max_length=20, choices=LEADER_SECTION_CHOICES, default=NOT_AVAILABLE
    )

    def __str__(self):
        return "{}: {}".format(self.section, self.preference)


class LeaderTripTypeChoice(models.Model):

    class Meta:
        unique_together = ('application', 'triptype')

    application = models.ForeignKey(
        'LeaderSupplement', on_delete=models.CASCADE
    )
    triptype = models.ForeignKey(
        TripType, on_delete=models.CASCADE
    )
    preference = models.CharField(
        max_length=20, choices=LEADER_TRIPTYPE_CHOICES, default=NOT_AVAILABLE
    )

    def __str__(self):
        return "{}: {}".format(self.triptype, self.preference)


class LeaderSupplement(DatabaseModel):
    """
    Leader application answers
    """
    NUMBER_OF_GRADES = 4

    objects = LeaderApplicationManager()

    section_choice = models.ManyToManyField(
        Section, through=LeaderSectionChoice
    )
    triptype_choice = models.ManyToManyField(
        TripType, through=LeaderTripTypeChoice
    )

    application = models.OneToOneField(
        GeneralApplication, editable=False, related_name='leader_supplement'
    )

    # Deprecated leader application
    _old_document = models.FileField(
        'leader application answers', blank=True, db_index=True
    )
    @property
    def deprecated_document(self):
        return self._old_document

    #  ------  trip and section availability ------
    _old_preferred_sections = models.ManyToManyField(
        Section, blank=True, related_name='preferred_leaders'
    )
    _old_available_sections = models.ManyToManyField(
        Section, blank=True, related_name='available_leaders'
    )
    _old_preferred_triptypes = models.ManyToManyField(
        TripType, blank=True, related_name='preferred_leaders',
        verbose_name='Preferred types of trips'
    )
    _old_available_triptypes = models.ManyToManyField(
        TripType, blank=True, related_name='available_triptypes',
        verbose_name='Available types of trips'
    )

    # ------- availibilty and experience --------

    availability = models.TextField(
        "Looking at the Trips descriptions, please feel free to use this "
        "space to address any concerns or explain your availability. If "
        "applicable, please also elaborate on any particular trips or "
        "activities that you absolutely CANNOT participate in. All "
        "information in this application will remain confidential.",
        blank=True
    )

    relevant_experience = models.TextField(
        'WITHOUT repeating anything you have already told us, please describe '
        'your level of expertise and any previous experience that you could '
        'bring to each trip type that you selected (e.g. lifeguard training, '
        'yoga experience, meditation experience, fishing experience, '
        'photography class, Walden enthusiast, NOLS, Cabin and Trail leader, '
        'etc).',
        blank=True
    )
    co_leader = models.TextField(
        'Please describe the qualities you would seek in an ideal co-leader. '
        'Be candid so we can best pair you.',
        blank=True
    )

    class_2_3_paddler = YesNoField(
        'Can you comfortably paddle Class II/III rapids?'
    )
    ledyard_level_1 = YesNoField(
        'Are you a Level I Ledyard whitewater kayaking leader or anticipate '
        'becoming one before the fall term?'
    )
    ledyard_level_2 = YesNoField(
        'Are you a Level II Ledyard whitewater kayaking leader or anticipate '
        'becoming one before the fall term?'
    )
    paddling_experience = models.TextField(
        'Please describe any kayaking or canoeing experience you have.',
        blank=True
    )
    climbing_course = YesNoField(
        'Have you taken a DOC-sponsored top rope course/anchor building '
        'course, or do you plan to take one before fall term?'
    )
    dmc_leader = YesNoField(
        'Are you a Dartmouth Mountaineering Club leader or will you become '
        'one before the fall term?'
    )
    climbing_experience = models.TextField(
        'Please describe any climbing experience you have.',
        blank=True
    )
    dmbc_leader = YesNoField(
        'Are you a leader in the Mountain Biking Club or will you become one '
        'before fall term?'
    )
    biking_experience = models.TextField(
        'Please describe any mountain biking experience you have.',
        blank=True
    )
    bike_maintenance_experience = models.TextField(
        'Please describe any experience you have with bike maintenance.',
        blank=True
    )
    cnt_leader = YesNoField(
        'Are you a Cabin and Trail leader or will you become one before the '
        'fall term?'
    )
    hiking_experience = models.TextField(
        'Please describe any hiking experience you have.',
        blank=True
    )

    def set_section_preference(self, section, preference):
        """Set the applicant's preference for a section."""
        LeaderSectionChoice.objects.create(
            application=self, section=section, preference=preference
        )

    def set_triptype_preference(self, triptype, preference):
        """Set the applicant's preference for a triptype."""
        LeaderTripTypeChoice.objects.create(
            application=self, triptype=triptype, preference=preference
        )

    def sections_by_preference(self, preference):
        qs = (self.leadersectionchoice_set
                .filter(preference=preference)
                .order_by('section')
                .select_related('section'))
        return [x.section for x in qs]

    def new_preferred_sections(self):
        return self.sections_by_preference(PREFER)

    def new_available_sections(self):
        return self.sections_by_preference(AVAILABLE)

    def triptypes_by_preference(self, preference):
        qs = (self.leadertriptypechoice_set
                .filter(preference=preference)
                .order_by('triptype')
                .select_related('triptype'))
        return [x.triptype for x in qs]

    def new_preferred_triptypes(self):
        return self.triptypes_by_preference(PREFER)

    def new_available_triptypes(self):
        return self.triptypes_by_preference(AVAILABLE)

    def get_preferred_trips(self):
        """
        All trips which this applicant prefers to lead
        """
        return (
            Trip.objects
            .filter(trips_year=self.trips_year)
            .filter(Q(section__in=self.new_preferred_sections()) &
                    Q(template__triptype__in=self.new_preferred_triptypes()))
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
            .filter(Q(section__in=self.new_preferred_sections()) |
                    Q(section__in=self.new_available_sections()),
                    Q(template__triptype__in=self.new_preferred_triptypes()) |
                    Q(template__triptype__in=self.new_available_triptypes()))
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

    # Deprecated croo application
    _old_document = models.FileField('Croo Application Answers', blank=True)

    @property
    def deprecated_document(self):
        return self._old_document

    # --- driving ------
    licensed = NullYesNoField(
        "Do you have a valid driver's license?"
    )
    college_certified = NullYesNoField(
        "Are you a college-certified driver?"
    )
    sprinter_certified = NullYesNoField(
        "Are you sprinter van certified?"
    )
    microbus_certified = NullYesNoField(
        "Are you microbus certified?"
    )
    can_get_certified = NullYesNoField(
        "If you are not certified, are you able to go through the "
        "College’s sprinter van & mini-bus driver certification process "
        "this spring or summer term?"
    )

    # --- croo positions ------
    safety_lead_willing = models.BooleanField(
        'Yes, I am willing to be a Safety Lead', default=False
    )
    kitchen_lead_willing = models.BooleanField(
        'Yes, I am willing to be a Kitchen Magician', default=False
    )
    kitchen_lead_qualifications = models.TextField(
        "If you are willing to be a Kitchen Magician, please briefly "
        "describe your qualifications for the position", help_text=(
            "(e.g. on Moosilauke Lodge crew spring 2014, experience "
            "working in industrial kitchens, experience preparing and "
            "organizing food for large groups)"
        ), blank=True
    )

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
