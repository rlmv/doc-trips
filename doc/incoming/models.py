import logging

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from doc.transport.models import Stop
from doc.trips.models import ScheduledTrip, Section, TripType
from doc.utils.choices import TSHIRT_SIZE_CHOICES, YES_NO_CHOICES
from doc.db.models import DatabaseModel
from doc.incoming.managers import IncomingStudentManager

logger = logging.getLogger(__name__)


def YesNoField(*args, **kwargs):
    # Use a boolean field instead?
    kwargs['choices'] = YES_NO_CHOICES
    kwargs['max_length'] = 3
    return models.CharField(*args, **kwargs)


class Address(models.Model):
    # TODO, or use django-address
    pass


class IncomingStudent(DatabaseModel):
    """
    Model to aggregate trippee information.

    Includes trippee input registration, college incoming student data, 
    database notes, and trip assignment.

    Created by the the post_save signal on Registration.

    TODO: call this IncomingStudent?
    """

    objects = IncomingStudentManager()

    registration = models.OneToOneField('Registration', editable=False,
                                        related_name='trippee', null=True)
    trip_assignment = models.ForeignKey(ScheduledTrip, on_delete=models.PROTECT,
                                        related_name='trippees', null=True)

    # TODO:
    # bus assignment
    # gear requested
    
    # TODO: decline_choices: sports, no responses, etc.
    decline_reason = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    # --- information provided by the college ----
    
    name = models.CharField(max_length=255)
    #    did = models.CharField(max_length=30)
    netid = models.CharField(max_length=20)
    class_year = models.CharField(max_length=10)

    # hmmmm no netid provided?
    # We may need to save did on the UserModel for matching registrations
    #    netid = models.CharField(max_len

    # address - related model ? or abstract.

    ethnic_code = models.CharField(max_length=1)
    gender = models.CharField(max_length=10)
    
    INCOMING_STATUS_CHOICES = (
        ('EXCHANGE', 'Exchange'),
        ('TRANSFER', 'Transfer'),
        ('FIRSTYEAR', 'First Year'),
    )
    incoming_status = models.CharField(max_length=20, choices=INCOMING_STATUS_CHOICES)

    # TODO: there is a lot of redundant email information floating around. 
    # can we get rid of some of it?
    email = models.EmailField(max_length=254)
    blitz = models.EmailField(max_length=254)

    def __str__(self):
        return self.name


class Registration(DatabaseModel):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)
    
    # name not just from netid / college info?
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=50)
    
    # contact could be in a related address model
    # which we could use for transport stops?
    # also, college input address info.
    # street1 = models.CharField(max_length=255)
    # street2 = models.CharField(

    previous_school = models.CharField('high school, or most recent school', max_length=255)
    home_phone = models.CharField(max_length=20, blank=True)
    cell_phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField('email address', max_length=254)
    guardian_email = models.EmailField('parent/guardian email', blank=True, max_length=254)

    # --- sections and triptypes -----
    # TODO: exchange/transfer/native/etc fields.
    # fall varsity athlete. --> choices or ForeignKey?
    is_exchange = YesNoField('Are you an Exchange Student?', blank=True)
    is_transfer = YesNoField('Are you a Transfer Student?', blank=True)
    is_international = YesNoField('Are you an International Student?', blank=True)
    is_native = YesNoField('Are you a Native American Student and plan on attending the Native American student orientation?', blank=True)
    is_fysep = YesNoField('Are you participating in the First Year Student Enrichment Program (FYSEP)?', blank=True)
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
    is_athlete = models.CharField('Are you a Fall varsity athlete (or Rugby or Water Polo)?', max_length=100, choices=ATHLETE_CHOICES, blank=True,  help_text="Each team has its own pre-season schedule. We are in close contact with fall coaches and will assign you to a trip section that works well for the team's pre-season schedule.")

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

    # section preferences
    schedule_conflicts = models.TextField(blank=True)
    # trip type preferences - they have a First Choice option in the old DB

    tshirt_size = models.CharField(max_length=2, choices=TSHIRT_SIZE_CHOICES)

    # ---- accomodations -----
    
    medical_conditions = models.TextField("Do you have any medical conditions, past injuries, disabilities or allergies that we should be aware of? Please describe any injury, condition, disability, or illness which we should take into consideration in assigning you to a trip", blank=True)
    allergies = models.TextField("Please describe any allergies you have (e.g. bee stings, specific medications, foods, etc.) which might require special medical attention.", blank=True)
    allergen_information = models.TextField("What happens if you come into contact with this allergen (e.g. I get hives, I go into anaphylactic shock)?", blank=True)
    
    needs = models.TextField("While many students manage their own health needs, we would prefer that you let us know of any other needs or conditions so we can ensure your safety and comfort during the trip.", blank=True)
    
    dietary_restrictions = models.TextField("Do you have any dietary restrictions we should be aware of (vegetarian, gluten-free, etc.)? We can accommodate ANY and ALL dietary needs as long as we know in advance. Leave blank if not applicable", blank=True)


    #  ----- physical condition and experience ------
    regular_exercise = YesNoField("Do you do enjoy cardiovascular exercise (running, biking, swimming, sports, etc.) on a regular basis?")
    physical_activities = models.TextField("Please describe the types of physical activities you enjoy, including frequency (daily? weekly?) and extent (number of miles or hours)", blank=True)
    other_activities = models.TextField("Do you do any other activities that might assist us in assigning you to a trip (yoga, karate, horseback riding, photography, fishing, etc.)?", blank=True)
    summer_plans = models.TextField("Please describe your plans for the summer (working at home, volunteering, etc.)", blank=True)

    SWIMMING_ABILITY_CHOICES = (
        ('NON_SWIMMER', 'Non-Swimmer'),
        ('BEGINNER', 'Beginner'),
        ('COMPETENT', 'Competent'),
        ('EXPERT', 'Expert'),
    )
    swimming_ability = models.CharField("Please rate yourself as a swimmer", max_length=20, choices=SWIMMING_ABILITY_CHOICES)
    
    camping_experience = YesNoField("Have you ever spent a night camping in the outdoors?")

    hiking_experience = YesNoField("Have you ever hiked or climbed with a pack of at least 20-30 pounds (10-15 kilograms)?")

    hiking_experience_description = models.TextField("Please describe your hiking experience. Where have you hiked? Was it mountainous or flat? Have you done day hikes? Have you hiked while carrying food and shelter with you? Please be specific: we want to physically challenge you as little or as much as you want. Be honest so that we can place you on the right trip for YOU. If you have questions about this, please let us know.", blank=True)

    has_boating_experience = YesNoField("Have you ever been on an overnight or extended canoe or kayak trip?", blank=True)
    boating_experience = models.TextField("Please describe your canoe or kayak trip experience. Have you paddled on flat water? Have you paddled on flat water? When did you do these trips and how long were they?", blank=True)
    other_boating_experience = models.TextField("Please describe any other paddling experience you have had. Be specific regarding location, type of water, and distance covered.", blank=True)

    fishing_experience = models.TextField("Please describe your fishing experience.", blank=True)
    
    horseback_riding_experience = models.TextField("Please describe your riding experience and ability level. What riding styles are you familiar with? How recently have you ridden horses on a regular basis? NOTE: Prior exposure and some experience is preferred for this trip.", blank=True)

    mountain_biking_experience = models.TextField("Please describe your biking experience and ability level. Have you done any biking off of paved trails? How comfortable are you riding on dirt and rocks?", blank=True)

    anything_else = models.TextField("Is there any other information you'd like to provide (anything helps!) that would assist us in assigning you to a trip?", blank=True)


    # ----- other deets ----

    # TODO: limit choices in the form to current trip_year and EXTRNAL stops
    bus_stop = models.ForeignKey(Stop, on_delete=models.PROTECT, 
                                 blank=True, null=True,
                                 verbose_name="Where would you like to be bussed from/to?")

    financial_assistance = YesNoField("Are you requesting financial assistance from DOC Trips? If 'yes' we will contact you in July with more information about your financial assistance.")
    waiver = YesNoField("I certify that I have read this assumption of risk and the accompanying registration materials. I approve participation for the student indicated above and this serves as my digital signature of this release, waiver & acknowledgement.")
    doc_membership = YesNoField("Would you like to purchase a DOC membership?")
    green_fund_donation = models.PositiveSmallIntegerField(blank=True, null=True)
    final_request = models.TextField("We know this form is really long, so thanks for sticking with us! The following question has nothing to do with your trip assignment. To whatever extent you feel comfortable, please share one thing you are excited and/or nervous for about coming to Dartmouth (big or small). There is no right or wrong answers &mdash; anything goes! All responses will remain anonymous.", blank=True)


@receiver(post_save, sender=Registration)
def connect_registration_to_trippee(instance=None, **kwargs):
    """
    When an incoming student submits a registration, try and 
    find the student's college-provided information and attach to 
    the registration.

    If the info cannot be found, the registration is left to sit.
    """
    if kwargs.get('created', False):
        try:
            instance.trippee = IncomingStudent.objects.get(
                netid=instance.user.netid,
                trips_year=instance.trips_year
            )
            instance.save()
        except IncomingStudent.DoesNotExist as e:
            msg = 'Incoming student info not found for registration %s'
            logger.info(msg % instance)
        
        
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
