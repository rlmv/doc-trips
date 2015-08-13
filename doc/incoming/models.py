import logging

from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator, MinValueValidator

from doc.transport.models import Stop, ExternalBus
from doc.trips.models import Trip, Section, TripType
from doc.utils.choices import TSHIRT_SIZE_CHOICES, YES_NO_CHOICES, YES
from doc.db.models import DatabaseModel
from doc.incoming.managers import IncomingStudentManager, RegistrationManager
from doc.users.models import NetIdField
from doc.core.models import Settings

logger = logging.getLogger(__name__)


def YesNoField(*args, **kwargs):
    # Use a boolean field instead?
    kwargs['choices'] = YES_NO_CHOICES
    kwargs['max_length'] = 3
    return models.CharField(*args, **kwargs)


class IncomingStudent(DatabaseModel):
    """
    Model to aggregate trippee information.
    
    All important logistical information is stored on this model 
    since it is possible for a student to go on a trip without 
    submitting a registration, but a student won't go on a trip
    unless we have received information from the college about her.

    Registrations and IncomingStudents are connected by post_save
    signals on each model.
    """

    objects = IncomingStudentManager()

    class Meta:
        unique_together = ('netid', 'trips_year')

    registration = models.OneToOneField(
        'Registration', editable=False, related_name='trippee', null=True
    )
    trip_assignment = models.ForeignKey(
        Trip, on_delete=models.PROTECT,
        related_name='trippees', null=True, blank=True
    )
    bus_assignment_round_trip = models.ForeignKey(
        Stop, on_delete=models.PROTECT, null=True, blank=True,
        related_name='riders_round_trip',
        verbose_name="bus assignment (round-trip)"
    )
    bus_assignment_to_hanover = models.ForeignKey(
        Stop, on_delete=models.PROTECT, null=True, blank=True,
        related_name='riders_to_hanover',
        verbose_name="bus assignment TO Hanover (one-way)"
    )
    bus_assignment_from_hanover = models.ForeignKey(
        Stop, on_delete=models.PROTECT, null=True, blank=True,
        related_name='riders_from_hanover',
        verbose_name="bus assignment FROM Hanover (one-way)"
    )

    financial_aid = models.PositiveSmallIntegerField(
        'percentage financial assistance',
        default=0, validators=[
            MinValueValidator(0), MaxValueValidator(100)
        ]
    )

    med_info = models.TextField(
        blank=True, help_text=(
            "Additional medical info not provided in the registration, "
            "or simplified information if some details do not need to be "
            "provided to leaders and croos."
        )
    )
    hide_med_info = models.BooleanField(
        "Hide registration med info?", default=False, help_text=(
            "Medical information in this trippee's registration "
            "will NOT be exported to leader and croo packets."
        )
    )

    # gear requested
    
    decline_reason = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    # --- information provided by the college ----
    
    name = models.CharField(max_length=512)
    netid = NetIdField()
    class_year = models.CharField(max_length=10)

    ethnic_code = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    birthday = models.CharField(max_length=20)
    
    INCOMING_STATUS_CHOICES = (
        ('EXCHANGE', 'Exchange'),
        ('TRANSFER', 'Transfer'),
        ('FIRSTYEAR', 'First Year'),
    )
    incoming_status = models.CharField(
        max_length=20, choices=INCOMING_STATUS_CHOICES, blank=True)

    email = models.EmailField(max_length=254)
    blitz = models.EmailField(max_length=254)
    phone = models.CharField(max_length=30)
    address = models.TextField()
 
    def get_registration(self):
        """ 
        Return this student's registration, or None if DNE 
        """
        try:
            return self.registration
        except ObjectDoesNotExist:
            return None

    def get_hometown(self):
        """
        Hack hack parse the town, state, and nation from address.
        """
        parts = self.address.split('\n')
        if len(parts) != 4:  # bad formatting - manually input?
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

    def bus_cost(self):
        """
        Compute the cost of buses for this student.

        There is either a round-trip bus or one-way buses,
        never both.
        """
        if self.bus_assignment_round_trip:
            return self.bus_assignment_round_trip.cost_round_trip

        one_way_cost = lambda x: x.cost_one_way if x else 0
        return (
            one_way_cost(self.bus_assignment_to_hanover) +
            one_way_cost(self.bus_assignment_from_hanover)
        )

    def compute_cost(self):
        """
        Compute the total charge for this student.
        
        Cost is the sum of the base cost, bus cost and
        doc membership, adjusted by financial aid, plus 
        any green fund donation.
        """
        costs = Settings.objects.get()
        base_cost = costs.trips_cost + self.bus_cost()

        reg = self.get_registration()
        if reg and reg.doc_membership == YES:
            base_cost += costs.doc_membership_cost
        green_fund = reg.green_fund_donation if reg else 0

        return (base_cost) * (100 - self.financial_aid) / 100 + green_fund

    def clean(self):
        """
        TODO: uncomment this
        one_way = (self.bus_assignment_to_hanover or
                   self.bus_assignment_from_hanover)
        if one_way and self.bus_assignment_round_trip:
            raise ValidationError(
                "Cannot have round-trip AND one-way bus assignments")
        """

    def delete_url(self):
        return reverse('db:incomingstudent_delete', kwargs=self.obj_kwargs())
        
    def detail_url(self):
        return reverse('db:incomingstudent_detail', kwargs=self.obj_kwargs())
        
    def __str__(self):
        return self.name


class Registration(DatabaseModel):
    """ 
    Registration information for an incoming student.
    """
    objects = RegistrationManager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)
    
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
    is_exchange = YesNoField('Are you an Exchange Student?', blank=True)
    is_transfer = YesNoField('Are you a Transfer Student?', blank=True)
    is_international = YesNoField(
        "Are you an International Student who plans on attending "
        "the International Student Orientation?",
        blank=True
    )
    is_native = YesNoField(
        "Are you a Native American Student who plans on attending "
        "the Native American student orientation?",
        blank=True
    )
    is_fysep = YesNoField(
        "Are you participating in the First Year Student Enrichment "
        "Program (FYSEP)?",
        blank=True
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
        max_length=100, choices=ATHLETE_CHOICES, blank=True,
        help_text=(
            "Each team has its own pre-season schedule. We are in close "
            "contact with fall coaches and will assign you to a trip section "
            "that works well for the team's pre-season schedule."
        )
    )

    preferred_sections = models.ManyToManyField(
        Section, blank=True, related_name='prefering_trippees'
    )
    available_sections = models.ManyToManyField(
        Section, blank=True, related_name='available_trippees'
    )
    unavailable_sections = models.ManyToManyField(
        Section, blank=True, related_name='unavailable_trippees'
    )
    firstchoice_triptype = models.ForeignKey(
        TripType, blank=True, null=True, related_name='firstchoice_triptype',
        verbose_name="first choice trip types",
    )
    preferred_triptypes = models.ManyToManyField(
        TripType, blank=True, related_name='preferring_trippees',
        verbose_name="preferred types of trips"
    )
    available_triptypes = models.ManyToManyField(
        TripType, blank=True, related_name='available_trippees',
        verbose_name="available types of trips"
    )
    unavailable_triptypes = models.ManyToManyField(
        TripType, blank=True, related_name='unavailable_trippees',
        verbose_name="unavailable trip types"
    )
    schedule_conflicts = models.TextField(blank=True)

    tshirt_size = models.CharField(max_length=2, choices=TSHIRT_SIZE_CHOICES)

    # ---- accomodations -----
    
    medical_conditions = models.TextField(
        "Do you have any medical conditions, past injuries, disabilities "
        "or allergies that we should be aware of? Please describe any "
        "injury, condition, disability, or illness which we should take "
        "into consideration in assigning you to a trip",
        blank=True
    )
    allergies = models.TextField(
        "Please describe any allergies you have (e.g. bee stings, specific "
        "medications, foods, etc.) which might require special medical "
        "attention.",
        blank=True
    )
    allergen_information = models.TextField(
        "What happens if you come into contact with this allergen (e.g. "
        "I get hives, I go into anaphylactic shock)?",
        blank=True
    )
    epipen = YesNoField(
        "Do you carry an EpiPen? If yes, please bring it with you on Trips.",
        blank=True
    )
    needs = models.TextField(
        "While many students manage their own health needs, we would prefer "
        "that you let us know of any other needs or conditions so we can "
        "ensure your safety and comfort during the trip (e.g. Diabetes, "
        "recent surgery, migraines).",
        blank=True
    )
    
    dietary_restrictions = models.TextField(
        "Do you have any dietary restrictions we should be aware of "
        "(vegetarian, gluten-free, etc.)? We can accommodate ANY and ALL "
        "dietary needs as long as we know in advance. Leave blank if not "
        "applicable",
        blank=True
    )
    SEVERITY_CHOICES = (
        (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)
    )
    allergy_severity = models.PositiveIntegerField(
        "If you have a food allergy, please rate the severity of the "
        "allergy on a scale from 1 to 5 (1 = itchy skin, puffy eyes and "
        "5 = anaphylaxis).",
        choices=SEVERITY_CHOICES, null=True, blank=True
    )
    allergy_reaction = models.TextField(
        "If you have a food allergy, please describe what happens when "
        "you come into contact with the allergen (e.g. I get hives, I go "
        "into anaphylactic shock).",
        blank=True
    )

    #  ----- physical condition and experience ------
    regular_exercise = YesNoField(
        "Do you do enjoy cardiovascular exercise (running, biking, "
        "swimming, sports, etc.) on a regular basis?"
    )
    physical_activities = models.TextField(
        "Please describe the types of physical activities you enjoy, "
        "including frequency (daily? weekly?) and extent (number of "
        "miles or hours)",
        blank=True
    )
    other_activities = models.TextField(
        "Do you do any other activities that might assist us in "
        "assigning you to a trip (yoga, karate, horseback riding, "
        "photography, fishing, etc.)?",
        blank=True
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
        max_length=20, choices=SWIMMING_ABILITY_CHOICES
    )
    
    camping_experience = YesNoField(
        "Have you ever spent a night camping under a tarp?"
    )
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
        blank=True
    )
    has_boating_experience = YesNoField(
        "Have you ever been on an overnight or extended canoe "
        "or kayak trip?",
        blank=True
    )
    boating_experience = models.TextField(
        "Please describe your canoe or kayak trip experience. Have you "
        "paddled on flat water? Have you paddled on flat water? When "
        "did you do these trips and how long were they?",
        blank=True
    )
    other_boating_experience = models.TextField(
        "Please describe any other paddling experience you have had. Be "
        "specific regarding location, type of water, and distance covered.",
        blank=True
    )
    fishing_experience = models.TextField(
        "Please describe your fishing experience.",
        blank=True
    )
    horseback_riding_experience = models.TextField(
        "Please describe your riding experience and ability level. What "
        "riding styles are you familiar with? How recently have you ridden "
        "horses on a regular basis? NOTE: Prior exposure and some "
        "experience is preferred for this trip.",
        blank=True
    )
    mountain_biking_experience = models.TextField(
        "Please describe your biking experience and ability level. Have "
        "you done any biking off of paved trails? How comfortable are you "
        "riding on dirt and rocks?",
        blank=True
    )
    sailing_experience = models.TextField(
        "Please describe your sailing experience.",
        blank=True
    )
    anything_else = models.TextField(
        "Is there any other information you'd like to provide (anything "
        "helps!) that would assist us in assigning you to a trip?",
        blank=True
    )

    # ----- other deets ----

    bus_stop_round_trip = models.ForeignKey(
        Stop, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name="Where would you like to be bussed from/to?",
        related_name='requests_round_trip',
    )
    bus_stop_to_hanover = models.ForeignKey(
        Stop, on_delete=models.PROTECT, blank=True, null=True,
        related_name='requests_to_hanover',
    )
    bus_stop_from_hanover = models.ForeignKey(
        Stop, on_delete=models.PROTECT, blank=True, null=True,
        related_name='requests_from_hanover',
    )

    financial_assistance = YesNoField(
        "Are you requesting financial assistance from DOC Trips? If "
        "'yes' we will contact you in July with more information about "
        "your financial assistance."
    )
    waiver = YesNoField(
        "I certify that I have read this assumption of risk and the "
        "accompanying registration materials. I approve participation "
        "for the student indicated above and this serves as my digital "
        "signature of this release, waiver and acknowledgement."
    )
    doc_membership = YesNoField(
        "Would you like to purchase a DOC membership?"
    )
    green_fund_donation = models.PositiveSmallIntegerField(
        default=0
    )
    final_request = models.TextField(
        "We know this form is really long, so thanks for sticking with "
        "us! The following question has nothing to do with your trip "
        "assignment. To whatever extent you feel comfortable, please "
        "share one thing you are excited and/or nervous for about coming "
        "to Dartmouth (big or small). There is no right or wrong answers "
        "&mdash; anything goes! All responses will remain anonymous.",
        blank=True
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
    def is_non_swimmer(self):
        return self.swimming_ability == self.NON_SWIMMER

    def _base_trips_qs(self):
        """ 
        Queryset to use for computing trip options for this registration.
        
        If the registration is NON_SWIMMER, exclude all swimming trips.
        """
        qs = (Trip.objects
              .filter(trips_year=self.trips_year)
              .filter(
                  models.Q(section__in=self.preferred_sections.all()) |
                  models.Q(section__in=self.available_sections.all()))
              .select_related('template__triptype', 'section')
              .order_by('template__triptype', 'section'))
        if self.is_non_swimmer:
            return qs.filter(template__non_swimmers_allowed=True)
        return qs
    
    def get_firstchoice_trips(self):
        """ 
        Return first choice Trips 
        
        For both preferred and available Sections
        """
        return self._base_trips_qs().filter(
            template__triptype=self.firstchoice_triptype
        )

    def get_preferred_trips(self):
        """ 
        Return preferred Trips 
        
        For both preferred and available Sections
        """
        return self._base_trips_qs().filter(
            template__triptype__in=self.preferred_triptypes.all()
        ).exclude(
            id__in=self.get_firstchoice_trips()
        )

    def get_available_trips(self):
        """ 
        Return available Trips 
        
        For both preferred and available Sections
        """
        return self._base_trips_qs().filter(
            template__triptype__in=self.available_triptypes.all()
        ).exclude(
            id__in=self.get_firstchoice_trips()
        ).exclude(
            id__in=self.get_preferred_trips()
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
                netid=self.user.netid,
                trips_year=self.trips_year
            )
            trippee.registration = self
            trippee.save()
            return trippee
        except IncomingStudent.DoesNotExist:
            msg = "student data not found for registration %s"
            logger.info(msg % self)
        

@receiver(post_save, sender=Registration)
def connect_registration_to_trippee(instance=None, **kwargs):
    """
    When an incoming student submits a registration, try and
    find the student's college-provided information and attach 
    to the registration.

    If the info cannot be found, the registration is left to sit.
    """
    if kwargs.get('created', False):
        instance.match()
        

@receiver(post_save, sender=IncomingStudent)
def create_trippee_for_college_info(instance=None, **kwargs):
    """ 
    If the incoming student has somehow already submitted a 
    registration, attach the registration to the new object.
    """
    if kwargs.get('created', False):
        try:
            instance.registration = Registration.objects.get(
                trips_year=instance.trips_year,
                user__netid=instance.netid
            )
            instance.save()
        except Registration.DoesNotExist:
            pass
