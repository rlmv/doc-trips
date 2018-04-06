import random
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import (
    Avg,
    Q,
    Case,
    Min,
    When,
    Count,
    OuterRef,
    Subquery,
    F,
    Count,
    Value as V
)
from django.utils import timezone
from django.utils.functional import cached_property

from .managers import QuestionManager, VolunteerManager, GraderManager

from fyt.core.models import DatabaseModel, TripsYear
from fyt.croos.models import Croo
from fyt.trips.models import Section, Trip, TripType
from fyt.users.models import DartmouthUser
from fyt.utils.cache import cache_as
from fyt.utils.choices import (
    AVAILABLE,
    NOT_AVAILABLE,
    PREFER,
    TSHIRT_SIZE_CHOICES,
)
from fyt.utils.model_fields import NullYesNoField, YesNoField
from fyt.utils.models import MedicalMixin
from fyt.utils.query import pks



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
        unique_together = ['index', 'trips_year']

    objects = QuestionManager()

    index = models.PositiveIntegerField(
        'order', help_text=(
            'change this value to re-order the questions'
        )
    )
    question = models.TextField(blank=False)

    ALL = 'ALL'
    LEADER = 'LEADER'
    CROO = 'CROO'
    OPTIONAL = 'OPTIONAL'
    TYPE_CHOICES = (
        (ALL, 'All applicants'),
        (LEADER, 'Leader applicants only'),
        (CROO, 'Croo applicants only'),
        (OPTIONAL, 'Optional')
    )
    type = models.CharField(
        'Is this a question for all applicants, leader applicants, croo '
        'applicants, or is it optional?',
        max_length=10, choices=TYPE_CHOICES, default=ALL
    )

    @property
    def leader_only(self):
        return self.type == self.LEADER

    @property
    def croo_only(self):
        return self.type == self.CROO

    @property
    def optional(self):
        return self.type == self.OPTIONAL

    @property
    def display_text(self):
        base_prefix = 'PLEASE ANSWER THIS IF YOU ARE APPLYING TO BE A {}. '

        if self.leader_only:
            prefix = base_prefix.format('TRIP LEADER')
        elif self.croo_only:
            prefix = base_prefix.format('CROOLING')
        elif self.optional:
            prefix = 'THIS QUESTION IS OPTIONAL. '
        else:
            prefix = ''

        return prefix + self.question

    def __str__(self):
        return "Question: {}".format(self.question)


def validate_word_count(value):
    if len(value.split()) > 300:
        raise ValidationError('Your answer must be less than 300 words long.')


class Answer(models.Model):
    """
    Through model for application answers.
    """
    class Meta:
        unique_together = ('application', 'question')
        ordering = ['question']

    application = models.ForeignKey(
        'Volunteer', on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE
    )
    answer = models.TextField(blank=True, validators=[validate_word_count])

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
        Given a Volunteer.status choice, return the description
        """
        return {
            Volunteer.PENDING: self.PENDING_description,
            Volunteer.CROO: self.CROO_description,
            Volunteer.LEADER: self.LEADER_description,
            Volunteer.LEADER_WAITLIST: self.LEADER_WAITLIST_description,
            Volunteer.REJECTED: self.REJECTED_description,
            Volunteer.CANCELED: self.CANCELED_description
        }[status]


def validate_condition_true(value):
    if value is not True:
        raise ValidationError('You must agree to this condition')


def validate_class_year(value):
    if value < 2000 or 2100 < value:
        raise ValidationError('Class year must look like 2017, 2020, etc.')


class ClassYearField(models.PositiveIntegerField):
    validators = [validate_class_year]


class Volunteer(MedicalMixin, DatabaseModel):
    """
    Contains shared information for Croo and Leader applications.
    """
    class Meta:
        ordering = ['applicant']
        unique_together = ['trips_year', 'applicant']

    # Maximum number of scores for an application
    NUM_SCORES = 3

    objects = VolunteerManager()

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
        settings.AUTH_USER_MODEL,
        editable=False,
        related_name='applications',
        on_delete=models.PROTECT
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
    # TODO: these fields are no longer used. All training data lives
    # in the `training` app, and the data held in these fields from
    # past years should be migrated to the training models.
    community_building = models.DateField(null=True, blank=True)
    risk_management = models.DateField(null=True, blank=True)
    wilderness_skills = models.DateField(null=True, blank=True)
    croo_training = models.DateField(null=True, blank=True)

    # ----- general information, not shown to graders ------
    class_year = ClassYearField()
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

    # TODO: migrate this data to the new gear app
    height = models.CharField(max_length=10, blank=True)

    # TODO: migrate this data to the new gear app
    weight = models.CharField(max_length=10, blank=True)

    # TODO: migrate this data to the new gear app
    gear = models.TextField(
        "Most trips require participants to have a frame pack, sleeping bag, "
        "and sleeping pad. What outdoor gear is available to you? Will you be "
        "able to borrow gear from friends and family or will you require "
        "rentals from DOC Trips?  While we will do our best to accommodate "
        "your gear needs if you are selected, priority will be given to "
        "first-years.",
        blank=True
    )

    hometown = models.CharField(max_length=255)
    academic_interests = models.CharField(
        'What do you like to study?', max_length=255, blank=True
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

    leader_willing = models.BooleanField(
        'I would like to be considered for a trip leader position.'
    )
    croo_willing = models.BooleanField(
        'I would like to be considered for a crooling position. (NOTE: '
        'students who are taking classes this sophomore summer can NOT apply, '
        'given the conflict of dates.)'
    )

    # ------ certs -------

    # TODO: this is not used post-2018
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
    # TODO: this is not used post-2018
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

    def required_questions_answered(self, type):
        """
        Returns True if all the required dynamic questions are answered, for
        the given type of question.
        """
        types = [Question.ALL, type]

        q_ids = set(q.id for q in self.required_questions() if q.type in types)

        for answer in self.answer_set.all():
            if answer.answer:  # "" is not an answer
                try:
                    q_ids.remove(answer.question_id)
                except KeyError:
                    pass

        return len(q_ids) == 0

    REQUIRED_QUESTIONS = '_required_questions'

    @cache_as(REQUIRED_QUESTIONS)
    def required_questions(self):
        """
        Used to cache this year's questions so that large querysets can be
        preloaded to improve efficiency.
        """
        return Question.objects.required(self.trips_year)

    @cache_as('_get_answers')
    def get_answers(self):
        return self.answer_set.all().select_related('question')

    @cache_as('_get_scores')
    def get_scores(self):
        return self.scores.all().select_related('grader')

    @property
    def leader_application_complete(self):
        """
        A leader application is complete if all questions are answered
        and the applicant has indicated that they want to be a leader.
        """
        return self.leader_willing and self.required_questions_answered(
            Question.LEADER)

    @property
    def croo_application_complete(self):
        """
        A croo application is complete if all questions are answered
        and the applicant has indicated that they want to be on a croo.
        """
        return self.croo_willing and self.required_questions_answered(
            Question.CROO)

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

    def add_score(self, grader, leader_score=None, croo_score=None, **kwargs):
        """
        Add a Score by `user` to the application.
        """
        return Score.objects.create(
            trips_year=self.trips_year,
            application=self,
            grader=grader,
            leader_score=leader_score,
            croo_score=croo_score,
            **kwargs
        )

    def skip(self, grader):
        """
        Skip this application in scoring.
        """
        return Skip.objects.create(
            trips_year=self.trips_year,
            application=self,
            grader=grader
        )

    @cached_property
    def _average_scores(self):
        return self.scores.aggregate(models.Avg('leader_score'),
                                     models.Avg('croo_score'))

    def average_leader_score(self):
        """Average leader score."""
        return self._average_scores['leader_score__avg']

    def average_croo_score(self):
        """Average croo score."""
        return self._average_scores['croo_score__avg']

    def first_aid_certifications_str(self):
        """Return a string of the volunteer's medical certifications.

        This provides a common access point to the free-form text medical
        certifications (prior to 2018), and the new foreign-key based info.
        """
        data = ['{}\n\n{}'.format(
            self.medical_certifications,
            self.medical_experience
        ).strip()] + [
            str(cert) for cert in self.first_aid_certifications.all()]

        return '\n'.join(filter(None, data))

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

    section_choice = models.ManyToManyField(
        Section, through=LeaderSectionChoice
    )
    triptype_choice = models.ManyToManyField(
        TripType, through=LeaderTripTypeChoice
    )

    application = models.OneToOneField(
        Volunteer,
        editable=False,
        related_name='leader_supplement',
        on_delete=models.PROTECT
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

    section_availability = models.TextField(
        'First-year students who plan to attend pre-orientation programs or are '
        'transfer/exchange students will be placed on particular sections, as '
        'indicated above. If you would like to lead a trip on a section with '
        'these students, please indicate your preference here.',
        blank=True
    )

    availability = models.TextField(
        "Looking at the Trips descriptions, please feel free to use this "
        "space to address any concerns or explain your availability. "
        "If applicable, please also elaborate on any particular trips or "
        "activities that you absolutely CANNOT participate in. All "
        "information in this application will remain confidential.",
        blank=True
    )

    relevant_experience = models.TextField(
        'WITHOUT repeating anything you have already told us, please describe '
        'your level of expertise and any previous experience that you could '
        'bring to each trip type that you selected (e.g. lifeguard training, '
        'yoga experience, meditation experience, fishing experience, '
        'photography class, Walden enthusiast, etc).',
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
            application=self,
            section=section,
            preference=preference)

    def set_triptype_preference(self, triptype, preference):
        """Set the applicant's preference for a triptype."""
        LeaderTripTypeChoice.objects.create(
            application=self,
            triptype=triptype,
            preference=preference)

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
                    Q(template__triptype__in=self.new_preferred_triptypes())))

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
            .exclude(id__in=self.get_preferred_trips().all()))

    def get_absolute_url(self):
        return self.application.get_absolute_url()

    def __str__(self):
        return str(self.application)


class CrooSupplement(DatabaseModel):
    """
    Croo application answers
    """

    application = models.OneToOneField(
        Volunteer,
        editable=False,
        related_name='croo_supplement',
        on_delete=models.PROTECT
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

    def get_absolute_url(self):
        return self.application.get_absolute_url()

    def __str__(self):
        return str(self.application)


class Score(DatabaseModel):
    """
    A score for a volunteer application.

    Note: this is a new model added in 2017 to replace LeaderApplicationGrade
    and CrooApplicationGrade which were used for split leader/croo applications.
    """
    class Meta:
        unique_together = ['grader', 'application']
        ordering = ['created_at']

    SCORE_CHOICES = (
        (1, "1 -- Bad application -- I really don't want this person to be a "
            "volunteer and I have serious concerns"),
        (1.5, "1.5"),
        (2, "2 -- Poor application -- I have some concerns about this person "
            "being a Trips volunteer"),
        (2.5, "2.5"),
        (3, "3 -- Fine application -- This person might work well as a "
            "volunteer but I have some questions"),
        (3.5, "3.5"),
        (4, "4 -- Good application -- I would consider this person to be a "
            "volunteer but I wouldn't be heartbroken if they were not "
            "selected"),
        (4.5, "4.5"),
        (5, "5 -- Great application -- I think this person would be a "
            "fantastic volunteer"),
    )

    grader = models.ForeignKey(
        'Grader',
        editable=False,
        related_name='scores',
        on_delete=models.PROTECT
    )
    application = models.ForeignKey(
        Volunteer,
        editable=False,
        related_name='scores',
        on_delete=models.PROTECT
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    # We save this as a field instead of referencing grader.permissions
    # so that we can remember this info even after permissions change.
    croo_head = models.BooleanField(
        'was the score created by a croo head?', default=False, editable=False
    )

    leader_score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        choices=SCORE_CHOICES,
        blank=True,
        null=True)

    croo_score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        choices=SCORE_CHOICES,
        blank=True,
        null=True)

    comments = models.ManyToManyField('ScoreQuestion', through='ScoreComment')

    general = models.TextField(
        "Given the notes you made above, please explain the holistic score "
        "that you assigned. If applicable, please note if the applicant is "
        "better qualified to be a trip leader or crooling, and please note "
        "any identities."
    )

    def clean(self):
        if (self.application.leader_application_complete and
                self.leader_score is None):
            raise ValidationError(
                {'leader_score': 'Score is required for leader applications'})

        if (self.application.croo_application_complete and
                self.croo_score is None):
            raise ValidationError(
                {'croo_score': 'Score is required for croo applications'})

    def save(self, **kwargs):
        """
        Set croo_head.
        """
        croo_head_perm = 'permissions.can_score_as_croo_head'

        if self.pk is None and self.grader.has_perm(croo_head_perm):
            self.croo_head = True

        return super().save(**kwargs)

    def add_comment(self, question, comment):
        """
        Add a comment to a specific answer.
        """
        return ScoreComment.objects.create(
            score=self, question=question, comment=comment)


class ScoreQuestion(DatabaseModel):
    """
    A question for graders to answer while scoring.
    """
    class Meta:
        ordering = ['order']

    question = models.TextField()
    order = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.question


class ScoreComment(models.Model):
    """
    A grader's comment on a specific answer.

    This is a M2M through model between Score and Answer.
    """
    score = models.ForeignKey(Score, on_delete=models.CASCADE)
    question = models.ForeignKey(ScoreQuestion, on_delete=models.PROTECT)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ['question']
        unique_together = ['score', 'question']

    def __str__(self):
        return self.comment


class Skip(DatabaseModel):
    """
    Marks an application as skipped.

    If a grader skips an application they will not be shown the application
    again.
    """
    class Meta:
        unique_together = ['grader', 'application']
        ordering = ['created_at']

    grader = models.ForeignKey(
        'Grader',
        editable=False,
        on_delete=models.CASCADE
    )
    application = models.ForeignKey(
        Volunteer,
        editable=False,
        related_name='skips',
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)


class ScoreClaim(DatabaseModel):
    """
    Marks an application as claimed to score by a grader.

    Once a claim exists on an application, the grader has X amount of time
    to finish scoring it before another grader will be given a chance.
    """
    #: The period of time to claim this score
    HOLD_DURATION = timedelta(hours=2)

    class Meta:
        ordering = ['claimed_at']

    grader = models.ForeignKey(
        'Grader',
        editable=False,
        related_name='score_claims',
        on_delete=models.CASCADE
    )
    application = models.ForeignKey(
        Volunteer,
        editable=False,
        related_name='score_claims',
        on_delete=models.CASCADE
    )
    croo_head = models.BooleanField(
       'is the grader a croo head?',
        default=False,
        editable=False
    )
    claimed_at = models.DateTimeField(default=timezone.now, editable=False)

    def save(self, **kwargs):
        """
        Set croo_head.
        """
        if self.pk is None:
            self.croo_head = self.grader.is_croo_head

        return super().save(**kwargs)


class Grader(DartmouthUser):
    """
    Proxy model for the basic user class.

    This provides a convenient place to stick logic related to individual
    graders.
    """
    class Meta:
        proxy = True

    objects = GraderManager()

    @cached_property
    def is_croo_head(self):
        return self.has_perm('permissions.can_score_as_croo_head')

    def claim_score(self, application):
        return ScoreClaim.objects.create(
            grader=self,
            application=application,
            trips_year=application.trips_year)

    def current_claim(self):
        """
        The current claim is an application that has a claim, and which the
        grader has not yet scored.

        Raise an error if there is more than one claim.
        """
        try:
            return self.score_claims.filter(
                claimed_at__gt=(timezone.now() - ScoreClaim.HOLD_DURATION)
            ).exclude(
                application__scores__grader=self
            ).get()
        except ScoreClaim.DoesNotExist:
            return None

    def scores_for_year(self, trips_year):
        return self.scores.filter(trips_year=trips_year)

    def score_count(self, trips_year):
        return self.scores_for_year(trips_year).count()

    def avg_leader_score(self, trips_year):
        return self.scores_for_year(trips_year).aggregate(
            Avg('leader_score'))['leader_score__avg']

    def avg_croo_score(self, trips_year):
        return self.scores_for_year(trips_year).aggregate(
            Avg('croo_score'))['croo_score__avg']

    def claim_next_to_score(self):
        """
        Find the next available application to score, and claim it.
        """
        if self.current_claim() is not None:
            claim = self.current_claim()
            # Update the claim time - this is for the case in which a grader
            # leaves the page, waits a while, then returns to grading,
            # receives the same application, but only has a few minutes
            # left to finish grading.
            claim.claimed_at = timezone.now()
            claim.save()
            return claim.application

        application = self.next_to_score()

        if application is None:
            return None

        self.claim_score(application)
        return application

    def next_to_score(self):
        """
        Return the next application for ``grader`` to score.

        This is an application which meets the following conditions:

        * is for the current trips_year
        * is complete
        * is PENDING
        * has not already been graded by this user
        * has not been skipped by this user
        * has been graded fewer than NUM_SCORES times

        Furthermore:
        * If the grader is a croo captain, prefer croo grades until each app
          has at least one score from a croo head.
        * Applications with fewer scores are prioritized.
        * Applications claims are included when counting scores for the
          application.
        """
        trips_year = TripsYear.objects.current()

        croo_app_pks = pks(Volunteer.objects.croo_applications(trips_year))

        NUM_SCORES = Volunteer.NUM_SCORES

        # Subquery for all active claims
        # TODO: use https://docs.djangoproject.com/en/2.0/ref/models/conditional-expressions/#conditional-aggregation
        active_claims_start = timezone.now() - ScoreClaim.HOLD_DURATION
        active_claims = ScoreClaim.objects.filter(
            application=OuterRef('pk'),
            claimed_at__gt=active_claims_start
        ).values('pk')

        qs = Volunteer.objects.leader_or_croo_applications(
            trips_year=trips_year
        ).filter(
            status=Volunteer.PENDING
        ).exclude(
            scores__grader=self
        ).exclude(
            skips__grader=self
        ).annotate(
            Count('scores')
        ).annotate(
            active_claims=Subquery(active_claims)
        ).annotate(
            Count('active_claims')
        ).annotate(
            scores_and_claims=F('scores__count') + F('active_claims__count')
        ).filter(
            scores_and_claims__lt=NUM_SCORES
        ).annotate(
            croo_head_scores=Count('pk', filter=Q(scores__croo_head=True)),
            croo_head_claims=Count('pk', filter=Q(
                score_claims__croo_head=True,
                score_claims__claimed_at__gt=active_claims_start)),
            needs_croo_score=TrueIf(
                pk__in=croo_app_pks,
                croo_head_scores=0,
                croo_head_claims=0
            )
        )

        # Croo head: try and pick a croo app which needs a croo head score
        if self.is_croo_head:
            needs_croo_head_score = qs.filter(needs_croo_score=True)
            if needs_croo_head_score.exists():
                qs = needs_croo_head_score

        # Otherwise, reserve one score on each app for a croo head
        else:
            qs = qs.filter(
                scores_and_claims__lt=Case(
                    When(needs_croo_score=True, then=V(NUM_SCORES-1)),
                    default=V(NUM_SCORES),
                    output_field=models.IntegerField()
                )
            )

        # Pick an app with least scores and claims
        # TODO: use a subquery
        qs = qs.filter(
            scores_and_claims=qs.aggregate(
                fewest=Min('scores_and_claims'))['fewest'])

        if not qs.exists():
            return None

        # Manually choose random element because .order_by('?') is buggy
        # See https://code.djangoproject.com/ticket/26390
        return random.choice(qs)

    # TODO: pass in claim directly? Validate current claim?
    def delete_claim(self, application):
        """
        Delete a claim - after scoring or skipping.
        """
        ScoreClaim.objects.filter(
            application=application,
            grader=self
        ).delete()


def TrueIf(**kwargs):
    """
    Return a case expression that evaluates to True if the query conditions
    are met, else False
    """
    return Case(
        When(then=True, **kwargs),
        default=False,
        output_field=models.BooleanField()
    )


# Deprecated models (contain historical data only)
# ----------------------------------------

class AbstractGrade(DatabaseModel):
    """
    Abstract model for shared grade information

    Concrete grade objects must implement an 'application' field
    """
    class Meta:
        abstract = True

    SCORE_CHOICES = (
        (1, "1 -- Bad application -- I really don't want this person to be a "
            "volunteer and I have serious concerns"),
        (2, "2 -- Poor application -- I have some concerns about this person "
            "being a Trips volunteer"),
        (3, "3 -- Fine application -- This person might work well as a "
            "volunteer but I have some questions"),
        (4, "4 -- Good application -- I would consider this person to be a "
            "volunteer but I wouldn't be heartbroken if they were not "
            "selected"),
        (5, "5 -- Great application -- I think this person would be a "
            "fantastic volunteer"),
        (6, "6 -- Incredible application -- I think this person should be one "
            "of the first to be selected to be a volunteer. I would be very "
            "frustrated/angry if this person is not selected"),
    )

    # related_name will be leaderapplicationgrades or crooapplicationgrades. Sweet.
    grader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False,
        related_name='%(class)ss',
        on_delete=models.PROTECT
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
        LeaderSupplement,
        related_name='grades',
        editable=False,
        on_delete=models.PROTECT
    )


class CrooApplicationGrade(AbstractGrade):
    """
    Grade for CrooApplications
    """
    application = models.ForeignKey(
        CrooSupplement,
        related_name='grades',
        editable=False,
        on_delete=models.PROTECT
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
    grader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False,
        on_delete=models.CASCADE)

    class Meta:
        abstract = True


class SkippedLeaderGrade(AbstractSkippedGrade):
    """
    Skipped leader application
    """
    application = models.ForeignKey(
        LeaderSupplement,
        editable=False,
        related_name='skips',
        on_delete=models.CASCADE
    )


class SkippedCrooGrade(AbstractSkippedGrade):
    """
    Skipped croo application
    """
    application = models.ForeignKey(
        CrooSupplement,
        editable=False,
        related_name='skips',
        on_delete=models.CASCADE
    )
    # marks whether the grader was grading for a particular
    # qualification when they skipped the application
    for_qualification = models.ForeignKey(
        QualificationTag,
        null=True,
        editable=False,
        on_delete=models.SET_NULL
    )
