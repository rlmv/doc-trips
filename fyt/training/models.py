from collections import OrderedDict

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from fyt.applications.models import Volunteer
from fyt.core.models import DatabaseModel
from fyt.training.managers import AttendeeManager


class Training(DatabaseModel):
    """
    A type of training.
    """
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Session(DatabaseModel):
    """
    A scheduled session for a certain training type.
    """
    class Meta:
        ordering = ['date', 'start_time', 'training']

    training = models.ForeignKey(Training, on_delete=models.PROTECT)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=256)

    # TODO: expose this as editable?
    DEFAULT_CAPACITY = 70

    def full(self):
        return self.registered.count() >= self.DEFAULT_CAPACITY

    def size(self):
        return self.registered.count()

    def registered_emails(self):
        """Emails for all registered attendees."""
        return self.registered.values_list(
            'volunteer__applicant__email', flat=True)

    # TODO: move to view
    def registered_emails_str(self):
        return "; ".join(self.registered_emails())

    def __str__(self):
        return "{}: {}, {} to {}".format(
            self.training,
            self.date.strftime('%B %d'),
            self.start_time.strftime('%l:%M %p'),
            self.end_time.strftime('%l:%M %p'))

    def update_attendance_url(self):
        return reverse('core:session:update_attendance',
                       kwargs=self.obj_kwargs())


class FirstAidCertification(DatabaseModel):
    """
    A first aid certification for a volunteer.
    """
    volunteer = models.ForeignKey(
        Volunteer,
        on_delete=models.PROTECT,
        related_name='first_aid_certifications')

    # First aid
    OTHER = 'other'
    CERTIFICATION_CHOICES = (
        (None, '--'),
        ('FA', 'First Aid'),
        ('CPR', 'CPR'),
        ('WFA', 'WFA'),
        ('WFR', 'WFR'),
        ('W-EMT', 'W-EMT'),
        ('EMT', 'EMT'),
        ('OEC', 'OEC'),
        (OTHER, 'other'),
    )
    name = models.CharField(
        'certification',
        max_length=10,
        blank=True,
        default="",
        choices=CERTIFICATION_CHOICES
    )
    other = models.CharField(
        max_length=100, blank=True, default=""
    )
    expiration_date = models.DateField()

    verified = models.BooleanField('verified?', default=False)

    class Meta:
        ordering = ['volunteer', 'pk']

    def get_name(self):
        if self.name == self.OTHER or not self.name:
            return self.other
        return self.name

    def __str__(self):
        return '{} (exp. {})'.format(self.get_name(),
                                     self.expiration_date.strftime('%x'))


class Attendee(DatabaseModel):
    """
    A volunteer attending trainings.
    """
    objects = AttendeeManager()

    class Meta:
        ordering = ['volunteer']

    volunteer = models.OneToOneField(Volunteer, on_delete=models.PROTECT)
    registered_sessions = models.ManyToManyField(
        Session, blank=True, related_name='registered')
    complete_sessions = models.ManyToManyField(
        Session, blank=True, related_name='completed')

    # TODO: migrate this data over to FirstAidCertification
    # First aid
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
    fa_cert = models.CharField(
        'first aid cert', max_length=10, blank=True, default="",
        choices=FIRST_AID_CHOICES
    )
    fa_other = models.CharField(
        'other first aid cert', max_length=100, blank=True, default=""
    )

    def get_first_aid_cert(self):
        if self.fa_cert == self.OTHER or not self.fa_cert:
            return self.fa_other
        return self.fa_cert

    def first_aid_complete(self):
        return bool(self.get_first_aid_cert())

    TRAINABLE_STATUSES = [
        Volunteer.LEADER,
        Volunteer.CROO,
        Volunteer.LEADER_WAITLIST]

    @property
    def can_register(self):
        return self.volunteer.status in self.TRAINABLE_STATUSES

    def __str__(self):
        return str(self.volunteer)

    def training_complete(self):
        """
        A volunteer has completed all trainings if they attended a session
        for each type of training.
        """
        return all(self.trainings_to_sessions().values())

    def trainings_to_sessions(self):
        trainings = Training.objects.filter(trips_year=self.trips_year)

        d = OrderedDict((t, None) for t in trainings)
        d.update({s.training: s for s in self.complete_sessions.all()})

        return d

    def detail_url(self):
        return self.volunteer.detail_url()


# TODO: move this to Volunteer.save?
@receiver(post_save, sender=Volunteer)
def create_attendee(instance=None, **kwargs):
    """
    Whenever a Volunteer is created, create a corresponding Attendee.
    """
    if kwargs.get('created', False):
        Attendee.objects.create(
            trips_year=instance.trips_year, volunteer=instance)
