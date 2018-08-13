from django.core.exceptions import ValidationError
from django.db import models

from .managers import GearRequestManager

from fyt.applications.models import Volunteer
from fyt.core.models import DatabaseModel
from fyt.incoming.models import IncomingStudent


class Gear(DatabaseModel):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class GearRequest(DatabaseModel):
    """
    A gear request is either attached to an IncomingStudent, or to a Volunteer.
    """
    class Meta:
        unique_together = [
            ('trips_year', 'incoming_student'),
            ('trips_year', 'volunteer')]
        ordering = ['incoming_student', 'volunteer']

    objects = GearRequestManager()

    # Gear requests
    # TODO: rename
    gear = models.ManyToManyField(Gear, blank=True)
    additional = models.TextField(blank=True)

    # Requested gear that will be provided to the trippee
    provided = models.ManyToManyField(Gear, blank=True,
                                      related_name="provided_to")
    provided_comments = models.TextField(
        'additional comments', blank=True, help_text=(
            'Add information here about why gear is not being provided, if applicable'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    incoming_student = models.OneToOneField(
        IncomingStudent,
        editable=False,
        null=True,
        related_name='gear_request',
        on_delete=models.PROTECT)

    volunteer = models.OneToOneField(
        Volunteer,
        editable=False,
        null=True,
        related_name='gear_request',
        on_delete=models.PROTECT)

    @property
    def requester(self):
        return self.incoming_student or self.volunteer

    @requester.setter
    def requester(self, user):
        try:
            self.incoming_student = IncomingStudent.objects.get(
                trips_year=self.trips_year, netid=user.netid)
        except IncomingStudent.DoesNotExist:
            pass
        try:
            self.volunteer = Volunteer.objects.get(
                trips_year=self.trips_year, applicant=user)
        except Volunteer.DoesNotExist:
            pass

    @property
    def role(self):
        if self.incoming_student:
            return 'TRIPPEE'
        return self.volunteer.status

    @property
    def email(self):
        if self.incoming_student:
            return self.incoming_student.get_email()
        return self.volunteer.applicant.email

    def clean(self):
        if self.incoming_student and self.volunteer:
            raise ValidationError('Only incoming students and trips volunteers '
                                  'may request gear.')

        if not self.incoming_student and not self.volunteer:
            raise ValidationError('Only incoming students and trips volunteers '
                                  'may request gear.')

    def __str__(self):
        return 'GearRequest ({})'.format(self.requester)
