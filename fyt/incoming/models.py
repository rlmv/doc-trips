import functools
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .managers import IncomingStudentManager, RegistrationManager

from fyt.core.models import DatabaseModel
from fyt.trips.models import Section, Trip, TripType
from fyt.users.models import NetIdField
from fyt.utils.choices import (
    AVAILABLE,
    FIRST_CHOICE,
    NOT_AVAILABLE,
    PREFER,
    TSHIRT_SIZE_CHOICES,
)
from fyt.utils.model_fields import NullYesNoField, YesNoField
from fyt.utils.models import MedicalMixin


def sort_by_lastname(students):
    """
    Sort an iterable of IncomingStudents by last name.
    """
    return sorted(students, key=lambda x: x.lastname)


def monetize(func):
    """
    Decorator which converts the return value of ``func`` to
    a :class:`~decimal.Decimal` with two decimal places.

    >>> identity = monetize(lambda x: x)
    >>> identity(1.2)
    Decimal('1.20')
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return Decimal(func(*args, **kwargs)).quantize(Decimal('.01'))

    return wrapper


class IncomingStudent(DatabaseModel):
    """
    Model to aggregate trippee information.

    All logistical information is stored on this model
    since it is possible for a student to go on a trip without
    submitting a registration, but a student won't go on a trip
    unless we have received information from the college about her.
    """

    objects = IncomingStudentManager()

    class Meta:
        unique_together = ['netid', 'trips_year']
        ordering = ['name']

    registration = models.OneToOneField(
        'Registration',
        editable=False,
        related_name='trippee',
        null=True,
        on_delete=models.PROTECT,
    )
    trip_assignment = models.ForeignKey(
        Trip, on_delete=models.PROTECT, related_name='trippees', null=True, blank=True
    )
    bus_assignment_round_trip = models.ForeignKey(
        'transport.Stop',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='riders_round_trip',
        verbose_name="bus assignment (round-trip)",
    )
    bus_assignment_to_hanover = models.ForeignKey(
        'transport.Stop',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='riders_to_hanover',
        verbose_name="bus assignment TO Hanover (one-way)",
    )
    bus_assignment_from_hanover = models.ForeignKey(
        'transport.Stop',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='riders_from_hanover',
        verbose_name="bus assignment FROM Hanover (one-way)",
    )
    financial_aid = models.PositiveSmallIntegerField(
        'percentage financial assistance',
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    cancelled = models.BooleanField(
        'cancelled last-minute?',
        default=False,
        help_text=(
            'This Trippee will still be charged even though '
            'they are no longer going on a trip'
        ),
    )
    cancelled_fee = models.PositiveSmallIntegerField(
        'cancellation fee',
        null=True,
        blank=True,
        help_text=(
            "Customize the cancellation fee. Otherwise a "
            "'cancelled' student is by default charged the full cost "
            "of trips (adjusted by financial aid, if applicable). "
        ),
    )
    med_info = models.TextField(
        'additional med info',
        blank=True,
        help_text=(
            "Use this field for additional medical info not provided in "
            "the registration, or simplified information if some details "
            "do not need to be provided to leaders and croos. This is always "
            "exported to leader packets."
        ),
    )
    hide_med_info = models.BooleanField(
        "Hide registration med info?",
        default=False,
        help_text=(
            "Checking this box will cause medical information in this "
            "trippee's registration to *not* be displayed in leader and croo "
            "packets."
        ),
    )

    decline_reason = models.CharField(max_length=50, blank=True)
    notes = models.TextField(
        "notes to trippee",
        blank=True,
        help_text=(
            "These notes are displayed to the trippee along "
            "with their trip assignment."
        ),
    )

    # --- information provided by the college ----

    name = models.CharField(max_length=512)
    netid = NetIdField()
    class_year = models.CharField(max_length=10)

    ethnic_code = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    birthday = models.CharField(max_length=20)

    EXCHANGE = 'EXCHANGE'
    TRANSFER = 'TRANSFER'
    FIRSTYEAR = 'FIRSTYEAR'
    INCOMING_STATUS_CHOICES = (
        (EXCHANGE, 'Exchange'),
        (TRANSFER, 'Transfer'),
        (FIRSTYEAR, 'First Year'),
    )
    incoming_status = models.CharField(
        max_length=20, choices=INCOMING_STATUS_CHOICES, blank=True
    )
    email = models.EmailField(max_length=254)
    blitz = models.EmailField(max_length=254)
    phone = models.CharField(max_length=30)
    address = models.TextField()
    hinman_box = models.CharField(max_length=50, blank=True)

    def get_registration(self):
        """
        Return this student's registration, or None if DNE
        """
        try:
            return self.registration
        except ObjectDoesNotExist:
            return None

    @property
    def lastname(self):
        """
        Parse last name from ``self.name``
        """
        return self.name.split()[-1]

    # TODO: store fields separately?
    def get_hometown(self):
        """
        Parse the town, state, and nation from ``self.address``.
        """
        parts = self.address.split('\n')
        if len(parts) != 4:  # unexpected formatting - manually input?
            return self.address
        city_state = ' '.join(parts[2].split(' ')[0:-1])
        return "%s %s" % (city_state, parts[3])

    def get_gender(self):
        """
        If there is a registration, pull gender from there.
        Otherwise use the incoming student data.
        """
        if self.get_registration():
            gender = self.get_registration().gender
        else:
            gender = self.gender
        return gender.lower()

    def get_phone_number(self):
        if self.get_registration():
            return self.get_registration().phone

        return self.phone

    def get_email(self):
        if self.get_registration():
            return self.get_registration().email
        return self.email

    def get_bus_to_hanover(self):
        return self.bus_assignment_round_trip or self.bus_assignment_to_hanover

    def get_bus_from_hanover(self):
        return self.bus_assignment_round_trip or self.bus_assignment_from_hanover

    @monetize
    def bus_cost(self):
        """
        Compute the cost of buses for this student.
        """

        def one_way_cost(x):
            if not x:
                return 0
            return x.cost_one_way

        if self.bus_assignment_round_trip:
            cost = self.bus_assignment_round_trip.cost_round_trip
        else:
            cost = one_way_cost(self.bus_assignment_to_hanover) + one_way_cost(
                self.bus_assignment_from_hanover
            )

        return self._adjust(cost)

    @monetize
    def trip_cost(self, costs):
        """
        Cost of trip assignment, if any, adjusted by financial aid.
        """
        if self.trip_assignment:
            return self._adjust(costs.trips_cost)
        return 0

    @monetize
    def cancellation_cost(self, costs):
        """
        Cost if a trippee cancels. Use a custom fee if provided,
        otherwise charge the regular cost of trips (adjusted by
        financial aid).
        """
        if not self.cancelled:
            return 0

        if self.cancelled_fee is None:
            return self._adjust(costs.trips_cost)
        else:
            return self.cancelled_fee

    @monetize
    def doc_membership_cost(self, costs):
        """
        Financial aid adjusted DOC membership cost, if elected.
        """
        reg = self.get_registration()
        if reg and reg.doc_membership:
            return self._adjust(costs.doc_membership_cost)
        return 0

    @monetize
    def green_fund_donation(self):
        """
        Trippee's donation to the green fund
        """
        reg = self.get_registration()
        return reg.green_fund_donation if reg else 0

    def _adjust(self, value):
        """
        Adjust a cost by this trippee's financial aid.
        """
        return value * (100 - self.financial_aid) / 100

    def compute_cost(self, costs=None):
        """
        Compute the total charge for this student.

        Cost is the sum of the base cost, bus cost and
        doc membership, adjusted by financial aid, plus
        any green fund donation and cancellation fees

        ``costs`` is a ``Settings`` instance
        """
        if costs is None:
            costs = Settings.objects.get(trips_year=self.trips_year)

        return sum(
            [
                self.trip_cost(costs),
                self.cancellation_cost(costs),
                self.bus_cost(),
                self.doc_membership_cost(costs),
                self.green_fund_donation(),
            ]
        )

    def clean(self):
        one_way = self.bus_assignment_to_hanover or self.bus_assignment_from_hanover
        if one_way and self.bus_assignment_round_trip:
            raise ValidationError("Cannot have round-trip AND one-way bus assignments")

    def save(self, **kwargs):
        """
        If the incoming student has somehow already submitted a
        registration, attach the registration to the new object.
        """
        if self.pk is None:  # new instance
            try:
                self.registration = Registration.objects.get(
                    trips_year=self.trips_year, user__netid=self.netid
                )
            except Registration.DoesNotExist:
                pass
        super().save(**kwargs)

    def __str__(self):
        return self.name


# TODO: test for 'True'
def validate_waiver(value):
    if not value:
        raise ValidationError("You must agree to the waiver")


REGISTRATION_SECTION_CHOICES = (
    (PREFER, 'prefer'),
    (AVAILABLE, 'available'),
    (NOT_AVAILABLE, 'not available'),
)

REGISTRATION_TRIPTYPE_CHOICES = (
    (FIRST_CHOICE, 'first choice'),
) + REGISTRATION_SECTION_CHOICES


# TODO: make abstract so that leader applications can also use this code
class RegistrationSectionChoice(models.Model):
    class Meta:
        unique_together = ('registration', 'section')

    registration = models.ForeignKey('Registration', on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    preference = models.CharField(
        max_length=20, choices=REGISTRATION_SECTION_CHOICES, default=NOT_AVAILABLE
    )

    def __str__(self):
        return "{}: {}".format(self.section, self.preference)


# TODO: make abstract so that leader applications can also use this code
class RegistrationTripTypeChoice(models.Model):
    class Meta:
        unique_together = ('registration', 'triptype')

    registration = models.ForeignKey('Registration', on_delete=models.CASCADE)
    triptype = models.ForeignKey(TripType, on_delete=models.CASCADE)
    preference = models.CharField(
        max_length=20, choices=REGISTRATION_TRIPTYPE_CHOICES, default=NOT_AVAILABLE
    )

    def __str__(self):
        return "{}: {}".format(self.triptype, self.preference)


class Registration(MedicalMixin, DatabaseModel):
    """
    Registration information for an incoming student.
    """

    section_choice = models.ManyToManyField(Section, through=RegistrationSectionChoice)
    triptype_choice = models.ManyToManyField(
        TripType, through=RegistrationTripTypeChoice
    )

    def set_section_preference(self, section, preference):
        RegistrationSectionChoice.objects.create(
            registration=self, section=section, preference=preference
        )

    def set_triptype_preference(self, triptype, preference):
        RegistrationTripTypeChoice.objects.create(
            registration=self, triptype=triptype, preference=preference
        )

    def sections_by_preference(self, preference):
        qs = (
            self.registrationsectionchoice_set.filter(preference=preference)
            .order_by('section')
            .select_related('section')
        )
        return [x.section for x in qs]

    def new_preferred_sections(self):
        return self.sections_by_preference(PREFER)

    def new_available_sections(self):
        return self.sections_by_preference(AVAILABLE)

    def new_unavailable_sections(self):
        return self.sections_by_preference(NOT_AVAILABLE)

    def triptypes_by_preference(self, preference):
        qs = (
            self.registrationtriptypechoice_set.filter(preference=preference)
            .order_by('triptype')
            .select_related('triptype')
        )
        return [x.triptype for x in qs]

    def new_firstchoice_triptypes(self):
        return self.triptypes_by_preference(FIRST_CHOICE)

    def new_preferred_triptypes(self):
        return self.triptypes_by_preference(PREFER)

    def new_available_triptypes(self):
        return self.triptypes_by_preference(AVAILABLE)

    def new_unavailable_triptypes(self):
        return self.triptypes_by_preference(NOT_AVAILABLE)

    objects = RegistrationManager()

    class Meta:
        ordering = ['name']
        unique_together = ['trips_year', 'user']

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, editable=False, on_delete=models.PROTECT
    )

    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=50)
    previous_school = models.CharField(
        'high school, or most recent school', max_length=255
    )
    phone = models.CharField('phone number', max_length=20)
    email = models.EmailField('email address', max_length=254)
    guardian_email = models.EmailField(
        'parent/guardian email', blank=True, max_length=254
    )

    # --- sections and triptypes -----
    is_exchange = NullYesNoField('Are you an Exchange Student?')

    is_transfer = NullYesNoField('Are you a Transfer Student?')

    is_international = NullYesNoField(
        "Are you an International Student who plans on attending "
        "the International Student Orientation?"
    )

    is_native = NullYesNoField(
        "Are you a Native American Student who plans on attending "
        "the Native American student orientation?"
    )

    is_fysep = NullYesNoField(
        "Are you participating in the First Year Student Enrichment " "Program (FYSEP)?"
    )

    ATHLETE_CHOICES = (
        ('NO', 'No'),
        ('ALPINE_SKIING', 'Alpine Skiing'),
        ('FOOTBALL', 'Football'),
        ('MENS_SOCCER', "Men's Soccer"),
        ('WOMENS_SOCCER', "Women's Soccer"),
        ('FIELD_HOCKEY', "Field Hockey"),
        ('VOLLEYBALL', "Volleyball"),
        ("MENS_HEAVYWEIGHT_CREW", "Men's Heavyweight Crew"),
        ("MENS_LIGHTWEIGHT_CREW", "Men's Lightweight Crew"),
        ("WOMENS_CREW", "Women's Crew"),
        ("MENS_CROSS_COUNTRY", "Men's Cross Country"),
        ("WOMENS_CROSS_COUNTRY", "Women's Cross Country"),
        ("MENS_GOLF", "Men's Golf"),
        ("WOMENS_GOLF", "Women's Golf"),
        ("MENS_TENNIS", "Men's Tennis"),
        ("WOMENS_TENNIS", "Women's Tennis"),
        ("MENS_RUGBY", "Men's Rugby"),
        ("WOMENS_RUGBY", "Women's Rugby"),
        ("SAILING", "Sailing"),
        ("MENS_WATER_POLO", "Men's Water Polo"),
    )
    is_athlete = models.CharField(
        "Are you a Fall varsity athlete (or Rugby or Water Polo)?",
        max_length=100,
        choices=ATHLETE_CHOICES,
        blank=True,
        help_text=(
            "Each team has its own pre-season schedule. We are in close "
            "contact with fall coaches and will assign you to a trip section "
            "that works well for the team's pre-season schedule."
        ),
    )

    # ------------------------------------------------------

    schedule_conflicts = models.TextField(blank=True)

    tshirt_size = models.CharField(max_length=3, choices=TSHIRT_SIZE_CHOICES)

    height = models.CharField(max_length=10, blank=True)
    weight = models.CharField(max_length=10, blank=True)

    #  ----- physical condition and experience ------

    regular_exercise = YesNoField(
        "Do you do enjoy cardiovascular exercise (running, biking, "
        "swimming, sports, etc.) on a regular basis?"
    )

    physical_activities = models.TextField(
        "Please describe the types of physical activities you enjoy, "
        "including frequency (daily? weekly?) and extent (number of "
        "miles or hours)",
        blank=True,
    )
    other_activities = models.TextField(
        "Do you do any other activities that might assist us in "
        "assigning you to a trip (yoga, karate, horseback riding, "
        "photography, fishing, etc.)?",
        blank=True,
    )

    NON_SWIMMER = 'NON_SWIMMER'
    BEGINNER = 'BEGINNER'
    COMPETENT = 'COMPETENT'
    EXPERT = 'EXPERT'
    SWIMMING_ABILITY_CHOICES = (
        (NON_SWIMMER, 'Non-Swimmer'),
        (BEGINNER, 'Beginner'),
        (COMPETENT, 'Competent'),
        (EXPERT, 'Expert'),
    )
    swimming_ability = models.CharField(
        "Please rate yourself as a swimmer",
        max_length=20,
        choices=SWIMMING_ABILITY_CHOICES,
    )

    camping_experience = YesNoField("Have you ever spent a night camping under a tarp?")

    hiking_experience = YesNoField(
        "Have you ever hiked or climbed with a pack of at "
        "least 20-30 pounds (10-15 kilograms)?"
    )

    hiking_experience_description = models.TextField(
        "Please describe your hiking experience. Where have you hiked? "
        "Was it mountainous or flat? Have you done day hikes? Have you "
        "hiked while carrying food and shelter with you? Please be "
        "specific: we want to physically challenge you as little or as "
        "much as you want. Be honest so that we can place you on the "
        "right trip for YOU. If you have questions about this, please "
        "let us know.",
        blank=True,
    )
    has_boating_experience = NullYesNoField(
        "Have you ever been on an overnight or extended canoe " "or kayak trip?"
    )
    boating_experience = models.TextField(
        "Please describe your canoe or kayak trip experience. Have you "
        "paddled on flat water? Have you paddled on flat water? When "
        "did you do these trips and how long were they?",
        blank=True,
    )
    other_boating_experience = models.TextField(
        "Please describe any other paddling experience you have had. Be "
        "specific regarding location, type of water, and distance covered.",
        blank=True,
    )
    fishing_experience = models.TextField(
        "Please describe your fishing experience.", blank=True
    )
    horseback_riding_experience = models.TextField(
        "Please describe your riding experience and ability level. What "
        "riding styles are you familiar with? How recently have you ridden "
        "horses on a regular basis? NOTE: Prior exposure and some "
        "experience is preferred for this trip.",
        blank=True,
    )
    mountain_biking_experience = models.TextField(
        "Please describe your biking experience and ability level. Have "
        "you done any biking off of paved trails? How comfortable are you "
        "riding on dirt and rocks?",
        blank=True,
    )
    sailing_experience = models.TextField(
        "Please describe your sailing experience.", blank=True
    )
    anything_else = models.TextField(
        "Is there any other information you'd like to provide (anything "
        "helps!) that would assist us in assigning you to a trip?",
        blank=True,
    )

    # ----- other deets ----

    bus_stop_round_trip = models.ForeignKey(
        'transport.Stop',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Where would you like to be bussed from/to?",
        related_name='requests_round_trip',
    )
    bus_stop_to_hanover = models.ForeignKey(
        'transport.Stop',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='requests_to_hanover',
    )
    bus_stop_from_hanover = models.ForeignKey(
        'transport.Stop',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='requests_from_hanover',
    )
    financial_assistance = YesNoField(
        "Are you requesting financial assistance from First-Year Trips? If "
        "'yes' we will contact you in July with more information about "
        "your financial assistance."
    )
    waiver = YesNoField(
        "I certify that I have read this assumption of risk and the "
        "accompanying registration materials. I approve participation "
        "for the student indicated above and this serves as my digital "
        "signature of this release, waiver and acknowledgement.",
        validators=[validate_waiver],
    )
    doc_membership = YesNoField("Would you like to purchase a DOC membership?")
    green_fund_donation = models.PositiveSmallIntegerField(default=0)
    final_request = models.TextField(
        "We know this form is really long, so thanks for sticking with "
        "us! The following question has nothing to do with your trip "
        "assignment. To whatever extent you feel comfortable, please "
        "share one thing you are excited and/or nervous for about coming "
        "to Dartmouth (big or small). There is no right or wrong answers "
        "&mdash; anything goes! All responses will remain anonymous.",
        blank=True,
    )

    # Added in 2019, hence the NULLable values
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def clean(self):
        one_way = self.bus_stop_to_hanover or self.bus_stop_from_hanover
        if self.bus_stop_round_trip and one_way:
            raise ValidationError(
                "You cannot select both a round-trip AND a one-way bus"
            )

    def get_trip_assignment(self):
        """
        Return the trip assignment for this registration's trippee.

        If the registration does not have an associated
        IncomingStudent, or IncomingStudent is not assigned
        to a trip, return None.
        """
        try:
            return self.trippee.trip_assignment
        except ObjectDoesNotExist:
            return None

    @property
    def netid(self):
        return self.user.netid

    @property
    def is_non_swimmer(self):
        return self.swimming_ability == self.NON_SWIMMER

    def _base_trips_qs(self):
        """
        Queryset to use for computing trip options for this registration.

        If the registration is NON_SWIMMER, exclude all swimming trips.
        """
        qs = (
            Trip.objects.filter(trips_year=self.trips_year)
            .filter(
                models.Q(section__in=self.new_preferred_sections())
                | models.Q(section__in=self.new_available_sections())
            )
            .select_related('template__triptype', 'section')
            .order_by('template__triptype', 'section')
        )
        if self.is_non_swimmer:
            return qs.exclude(template__swimtest_required=True)
        return qs

    def get_firstchoice_trips(self):
        """
        Return first choice Trips

        For both preferred and available Sections
        """
        return self._base_trips_qs().filter(
            template__triptype__in=self.new_firstchoice_triptypes()
        )

    def get_preferred_trips(self):
        """
        Return preferred Trips

        For both preferred and available Sections
        """
        return self._base_trips_qs().filter(
            template__triptype__in=self.new_preferred_triptypes()
        )

    def get_available_trips(self):
        """
        Return available Trips

        For both preferred and available Sections
        """
        return self._base_trips_qs().filter(
            template__triptype__in=self.new_available_triptypes()
        )

    def get_incoming_student(self):
        """
        Return this registration's IncomingStudent, or None if DNE
        """
        try:
            return self.trippee
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return self.name

    def match(self):
        """
        Try to match this registration with incoming student data.

        Returns the matched IncomingStudent, or None.
        """
        try:
            trippee = IncomingStudent.objects.get(
                netid=self.user.netid, trips_year=self.trips_year
            )
            trippee.registration = self
            trippee.save()
            return trippee
        except IncomingStudent.DoesNotExist:
            pass

    def save(self, **kwargs):
        """
        When an incoming student submits a registration, try and
        find the student's college-provided information and attach
        to the registration.

        If the info cannot be found, the registration is left to sit.
        """
        created = self.pk is None
        super().save(**kwargs)
        if created:
            self.match()


class Settings(DatabaseModel):
    """
    Contains global configuration values that appear across the site
    """

    trips_cost = models.PositiveSmallIntegerField()
    doc_membership_cost = models.PositiveSmallIntegerField()
    contact_url = models.URLField(help_text='url of trips directorate contact info')

    class Meta:
        unique_together = ['trips_year']
