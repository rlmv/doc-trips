from django.db import models

from .model_fields import NullYesNoField


LEAVE_BLANK = "Leave blank if not applicable"


class MedicalMixin(models.Model):
    """
    Medical information shared by GeneralApplications and IncomingStudents
    """
    class Meta:
        abstract = True

    food_allergies = models.TextField(
        "Please list any food allergies you have "
        "(e.g. peanuts, shellfish). Describe what happens when you come "
        "into contact with this allergen (e.g. 'I get hives,' 'I go into "
        "anaphylactic shock').",
        blank=True, help_text=LEAVE_BLANK
    )
    dietary_restrictions = models.TextField(
        "Do you have any other dietary restrictions we should be aware of "
        "(e.g. vegetarian, gluten-free, etc.)? We can accommodate ANY and ALL "
        "dietary needs as long as we know in advance.",
        blank=True, help_text=LEAVE_BLANK
    )
    medical_conditions = models.TextField(
        "Do you have any other medical conditions, past injuries, disabilities "
        "or other allergies that we should be aware of? Please describe any "
        "injury, condition, disability, or illness which we should take "
        "into consideration in assigning you a trip",
        blank=True, help_text=LEAVE_BLANK
    )
    epipen = NullYesNoField(
        "Do you carry an EpiPen? If yes, please bring it with you on Trips.",
        blank=True
    )
    needs = models.TextField(
        "While many students manage their own health needs, we would prefer "
        "that you let us know of any other needs or conditions so we can "
        "ensure your safety and comfort during the trip (e.g. Diabetes, "
        "recent surgery, migraines).",
        blank=True, help_text=LEAVE_BLANK
    )

    def clear_medical_info(self):
        """
        Clear all medical information on the object.

        Does not persist the changes -- you must call ``save``.
        """
        self.food_allergies = ''
        self.dietary_restrictions = ''
        self.medical_conditions = ''
        self.epipen = None
        self.needs = ''
