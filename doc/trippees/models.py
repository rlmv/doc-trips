import logging

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from doc.transport.models import Stop
from doc.trips.models import ScheduledTrip
from doc.utils.choices import TSHIRT_SIZE_CHOICES, YES_NO_CHOICES
from doc.db.models import DatabaseModel

logger = logging.getLogger(__name__)

def YesNoField(*args, **kwargs):
    # Use a boolean field instead?
    kwargs['choices'] = YES_NO_CHOICES
    kwargs['max_length'] = 2
    return models.CharField(*args, **kwargs)
    

class Address(models.Model):
    # TODO, or use django-address
    pass

class Trippee(DatabaseModel):
    """
    Model to aggregate trippee information.

    Includes trippee input registration, college incoming student data, 
    database notes, and trip assignment.

    Created by the the post_save signal on TrippeeRegistration.
    """

    registration = models.OneToOneField('TrippeeRegistration', editable=False,
                                        related_name='trippee', null=True)
    info = models.OneToOneField('CollegeInfo', editable=False,
                                related_name='trippee')
    trip_assignment = models.ForeignKey(ScheduledTrip, on_delete=models.PROTECT,
                                        related_name='trippees', null=True)

    # TODO:
    # bus assignment
    # gear requested
    
    # TODO: decline_choices: sports, no responses, etc.
    decline_reason = models.CharField(max_length=50, blank=True)

    notes = models.TextField(blank=True)
    

class CollegeInfo(DatabaseModel):
    """
    Trippee information provided by the college.
    """
    
    name = models.CharField(max_length=255)
    #    did = models.CharField(max_length=30)
    netid = models.CharField(max_length=20)

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
    dartmouth_email = models.EmailField(max_length=254)
    

class TrippeeRegistration(DatabaseModel):

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
    home_phone = models.CharField(max_length=20)
    cell_phone = models.CharField(max_length=20)
    email = models.EmailField('email address', max_length=254)
    guardian_email = models.EmailField('parent/guardian email', max_length=254)
    
    # TODO: exchange/transfer/native/etc fields.
    # fall varsity athlete. --> choices or ForeignKey?
    
    # TODO: section and triptypes prefs -> custom model? custom field?
    # section preferences 
    schedule_conflicts = models.TextField(blank=True)
    # trip type preferences - they have a First Choice option in the old DB

    tshirt_size = models.CharField(max_length=2, choices=TSHIRT_SIZE_CHOICES)
    
    # ---- accomodations -----
    
    medical_conditions = models.TextField("Do you have any medical conditions, past injuries, disabilities or allergies that we should be aware of? Please describe any injury, condition, disability, or illness which we should take into consideration in assigning you to a trip")
    allergies = models.TextField("Please describe any allergies you have (e.g. bee stings, specific medications, foods, etc.) which might require special medical attention.")
    allergen_information = models.TextField("What happens if you come into contact with this allergen (e.g. I get hives, I go into anaphylactic shock)?")
    
    needs = models.TextField("While many students manage their own health needs, we would prefer that you let us know of any other needs or conditions so we can ensure your safety and comfort during the trip.")
    
    dietary_restrictions = models.TextField("Do you have any dietary restrictions we should be aware of (vegetarian, gluten-free, etc.)? We can accommodate ANY and ALL dietary needs as long as we know in advance. Leave blank if not applicable")


    #  ----- physical condition and experience ------
    regular_exercise = models.CharField(max_length=2, choices=YES_NO_CHOICES)
    physical_activities = models.TextField("Please describe the types of physical activities you enjoy, including frequency (daily? weekly?) and extent (number of miles or hours)")
    other_activities = models.TextField("Do you do any other activities that might assist us in assign you to a trip (yoga, karate, horseback riding, photography, fishing, etc.)?")
    summer_plans = models.TextField("Please describe your plans for the summer (working at home, volunteering, etc.)")

    SWIMMING_ABILITY_CHOICES = (
        ('NON_SWIMMER', 'Non-Swimmer'),
        ('BEGINNER', 'Beginner'),
        ('COMPETENT', 'Competent'),
        ('EXPERT', 'Expert'),
    )
    swimming_ability = models.CharField(max_length=20, choices=SWIMMING_ABILITY_CHOICES)
    
    camping_experience = YesNoField("Have you ever spent a night camping in the outdoors?")

    hiking_experience = YesNoField("Have you ever hiked or climbed with a pack of at least 20-30 pounds (10-15 kilograms)?")

    hiking_experience_description = models.TextField("Please describe your hiking experience. Where have you hiked? Was it mountainous or flat? Have you done day hikes? Have you hiked while carrying food and shelter with you? Please be specific: we want to physically challenge you as little or as much as you want. Be honest so that we can place you on the right trip for YOU. If you have questions about this, please let us know.", blank=True)

    has_boating_experience = YesNoField("Have you ever been on an overnight or extended canoe or kayak trip?")
    boating_experience = models.TextField("Please describe your canoe or kayak trip experience. Have you paddled on flat water? Have you paddled on flat water? When did you do these trips and how long were they?")
    other_boating_experience = models.TextField("Please describe any other paddling experience you have had. Be specific regarding location, type of water, and distance covered.")

    fishing_experience = models.TextField("Please describe your fishing experience.")
    
    horseback_riding_experience = models.TextField("Please describe your riding experience and ability level. What riding styles are you familiar with? How recently have you ridden horses on a regular basis? NOTE: Prior exposure and some experience is preferred for this trip.")

    mountain_biking_experience = models.TextField("Please describe your biking experience and ability level. Have you done any biking off of paved trails? How comfortable are you riding on dirt and rocks?")

    anything_else = models.TextField("Is there any other information you'd like to provide (anything helps!) that would assist us in assigning you to a trip?")


    # ----- other deets ----

    # TODO: limit choices in the form to current trip_year and EXTRNAL stops
    bus_stop = models.ForeignKey(Stop, on_delete=models.PROTECT, 
                                 verbose_name="Where would you like to be bussed from/to?")

    financial_assistance = YesNoField("Are you requesting financial assistance from DOC Trips? If 'yes' we will contact you in July with more information about your financial assistance.")
    waiver = YesNoField("I certify that I have read this assumption of risk and the accompanying registration materials. I approve participation for the student indicated above and this serves as my digital signature of this release, waiver & acknowledgement.")
    doc_membership = YesNoField()
    green_fund_donation = models.PositiveSmallIntegerField()
    final_request = models.TextField("We know this form is really long, so thanks for sticking with us! The following question has nothing to do with your trip assignment. To whatever extent you feel comfortable, please share one thing you are excited and/or nervous for about coming to Dartmouth (big or small). There is no right or wrong answers - anything goes! All responses will be remain anonymous.")


@receiver(post_save, sender=TrippeeRegistration)
def connect_registration_to_trippee(instance=None, **kwargs):
    """
    When an incoming student submits a registration, try and 
    find the student's college-provided information and attach to 
    the registration.

    If the info cannot be found, the registration is left to sit.
    """
    if kwargs.get('created', False):
        try:
            instance.trippee = Trippee.objects.get(
                info__did=instance.user.did,
                trips_year=instance.trips_year
            )
            instance.save()
        except Trippee.DoesNotExist as e:
            msg = 'Incoming student info not found for registration %s'
            logger.info(msg % instance)
        
        
@receiver(post_save, sender=CollegeInfo)
def create_trippee_for_college_info(instance=None, **kwargs):
    """ 
    When incoming student info is added to the database, 
    connect an administrative Trippee object.

    If the incoming student has somehow already submitted a 
    registration, attach the registration to the new Trippee
    object.
    """
    
    if kwargs.get('created', False):
        trippee = Trippee.objects.create(
            trips_year=instance.trips_year,
            info=instance
        )
        try:
            existing_reg = TrippeeRegistration.objects.get(
                trips_year=instance.trips_year,
                user__did=instance.did
            )
            trippee.registration = existing_reg
            trippee.save()
        except TrippeeRegistration.DoesNotExist:
            pass
