
from django.db import models
from django.conf import settings

from db.models import DatabaseModel
from trips.models import ScheduledTrip, Section, TripType
from croos.models import Croo

# TODO: move to globals and reuse for trippees
TSHIRT_SIZE_CHOICES = (
    ('S', 'Small'), 
    ('M', 'Medium'), 
    ('L', 'Large'), 
    ('XL', 'Extra large'),
)


class GeneralApplication(DatabaseModel):

    # ---- administrative information. not seen by applicants ------
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL)
#    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=PENDING#, 
#                              verbose_name="Application status")

    # ----- general information, not shown to graders ------
    class_year = models.PositiveIntegerField()
    gender = models.CharField(max_length=25)
    race_ethnicity = models.CharField('race/ethnicity', max_length=255, blank=True, help_text='optional')
    hinman_box = models.CharField(max_length=10)
    phone = models.CharField('cell phone number', blank=True, max_length=255)
    summer_address = models.CharField(blank=True, max_length=255, help_text="don't worry if you don't know yet")
    tshirt_size = models.CharField(max_length=2, choices=TSHIRT_SIZE_CHOICES)

    # ------- -------
    from_where = models.CharField('Where are you from?', max_length=255)
    what_do_you_like_to_study = models.CharField('What do you like to study?', max_length=255)
    personal_activities = models.TextField(blank=True, verbose_name='Please list your primary activities and involvements at Dartmouth and beyond')
    feedback = models.TextField(blank=True, verbose_name="If you have any experience with Trips, what would you change about the program (big or small)?  If you do not have experience with Trips, what would you change about the program OR what would you change about your introduction to Dartmouth?")

    # ------ dietary --------
    dietary_restrictions = models.TextField(blank=True, verbose_name="Do you have any dietary restrictions or allergies that we should know about?")
    allergen_information = models.TextField(blank=True, verbose_name="What happens if you come into contact with this allergen (e.g. I turn purple and squishy if I eat a grape!)?")

    # ------ certs -------
    medical_certifications = models.TextField(blank=True)
    medical_experience = models.TextField(blank=True, verbose_name="Briefly describe your experience with your safety certifications. How frequently do you use your certification and in what circumstances?")
    peer_training = models.TextField(blank=True, verbose_name="If you have participated in or lead a peer training program, such as DPP, IGD, DBI, MAV, EDPA, SAPA, DAPA, UGA, etc. please list them here, and briefly describe them.")

    # ------- notices -------
    trippee_confidentiality = models.BooleanField(default=False, verbose_name="If selected to be a DOC Trips Leader, I understand that I will be given access to my Trippees' confidential medical information for safety purposes. I pledge to maintain the confidentiality of this information, except as is required by medical or legal concerns")
    in_goodstanding_with_college = models.BooleanField(default=False, verbose_name="By applying to lead a DOC Trip, I acknowledge that I am in good standing with the College. This may be verified by DOC Trips through the Undergraduate Dean’s Office.")
    trainings = models.BooleanField(default=False, verbose_name="I understand that if I am accepted as a crooling or trip leader I will be required to get First Aid and CPR training, as well as attend croo and leader specific training. I understand that if I do not meet these requirements, I will not be able to be on a croo/lead a trip.")
    spring_training_ok = models.BooleanField(default=False, verbose_name="I can attend trainings during the spring term.")
    summer_training_ok = models.BooleanField(default=False, verbose_name="I can attend trainings during the summer term.")


class LeaderSupplement(DatabaseModel):

    application = models.OneToOneField('GeneralApplication')
    file = models.FileField()

    #  ------  trip and section information ------
    preferred_sections = models.ManyToManyField(Section, blank=True,
                                                related_name='preferred_leaders')
    available_sections = models.ManyToManyField(Section, blank=True,
                                                related_name='available_leaders')
    preferred_triptypes = models.ManyToManyField(TripType, blank=True,
                                                 related_name='preferred_leaders',
                                                 verbose_name='Preferred types of trips')
    available_triptypes = models.ManyToManyField(TripType, blank=True, 
                                                 related_name='available_triptypes', 
                                                 verbose_name='Available types of trips')

    # ------- availibilty and experience --------
    trip_preference_comments = models.TextField(blank=True, verbose_name="Looking at the Trips descriptions, please feel free to use this space to address any concerns or explain your availability. This will only be used to help us in Trip assignments, it will not be considered when your application is being read.")
    cannot_participate_in = models.TextField(blank=True, verbose_name="If applicable, please elaborate (to the extent you feel comfortable) on any particular trips or activities that you absolutely cannot participate in. This information will be used exclusively for trip assignments & co-leader pairings. All information in this application will remain confidential.")
    experience = models.TextField(blank=True, verbose_name="For each type of trip you are interested in leading, please describe your level of expertise and any amount of previous experience that might qualify you to lead that particular trip (DOC Wilderness Leader, lifeguard training, yoga experience, mountain biking enthusiast, photography class, NOLS, etc.).")
    
    # ----- trainings -----
    community_building = models.DateField(null=True, blank=True)
    risk_management = models.DateField(null=True, blank=True)
    wilderness_skills = models.DateField(null=True, blank=True)
    first_aid = models.DateField('First Aid/CPR', null=True, blank=True)


class CrooSupplement(DatabaseModel):

    application = models.OneToOneField('GeneralApplication')
    file = models.FileField()

    assigned_croo = models.ForeignKey(Croo, blank=True, null=True, 
                                      related_name='croolings',
                                      on_delete=models.SET_NULL)
    potential_croos = models.ManyToManyField(Croo, blank=True, 
                                             related_name='potential_croolings')

    safety_dork_qualified = models.BooleanField(default=False)
    safety_dork = models.BooleanField(default=False)
    
