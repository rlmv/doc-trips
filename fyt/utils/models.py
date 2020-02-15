from django.db import models

from .model_fields import NullYesNoField


LEAVE_BLANK = "Leave blank if not applicable"


class MedicalMixin(models.Model):
    """
    Medical information shared by Volunteers and IncomingStudents
    """

    class Meta:
        abstract = True

    food_allergies = models.TextField(
        "Please list any food allergies you have "
        "(e.g. peanuts, shellfish). Describe what happens when you come "
        "into contact with this allergen (e.g. 'I get hives,' 'I go into "
        "anaphylactic shock').",
        blank=True,
        help_text=LEAVE_BLANK,
    )
    dietary_restrictions = models.TextField(
        "Do you have any other dietary restrictions we should be aware of "
        "(e.g. vegetarian, gluten-free, etc.)? We can accommodate ANY and ALL "
        "dietary needs as long as we know in advance.",
        blank=True,
        help_text=LEAVE_BLANK,
    )
    medical_conditions = models.TextField(
        "Do you have any other medical conditions, past injuries, ability-related concerns, "
        "other allergies, or personal concerns (regarding your own physical/mental/emotional health) "
        "that would be relevant to your role as a trip leader or crooling (in trip placement, "
        "completing trainings, participating in a croo, etc.)? This information is requested "
        "to help us place you in a position you feel comfortable. Again, this entire section "
        "will not be considered during the grading of your application.",
        blank=True,
        help_text=LEAVE_BLANK,
    )
    epipen = NullYesNoField(
        "Do you carry an EpiPen? If yes, please bring it with you on Trips.", blank=True
    )
    needs = models.TextField(
        "While many students manage their own health needs, we would prefer "
        "that you let us know of any other needs or conditions so we can "
        "ensure your safety and comfort during the trip (e.g. Diabetes, "
        "recent surgery, migraines).",
        blank=True,
        help_text=LEAVE_BLANK,
    )
