import math
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from model_utils import FieldTracker

from .managers import (
    CampsiteManager,
    SectionDatesManager,
    SectionManager,
    TripManager,
    TripTypeManager,
)

from fyt.core.models import DatabaseModel
from fyt.utils.cache import cache_as


"""
TODO: use these in place of magic numbers?
INTVL_LEADERS = timedelta(days=0)
INTVL_TRIPPEES = timedelta(days=1)
INTVL_CAMPSITE_1
INTVL_CAMPSITE_2
INTVL_LODGE
INTVL_CAMPUS
"""

NUM_BAGELS_REGULAR = 1.3  # number of bagels per person
NUM_BAGELS_SUPPLEMENT = 1.6  # number of bagels for supplemental trip


class Trip(DatabaseModel):
    """
    The core object representing a scheduled trip.

    Once a Trip has been instantiated in the database, it's section and
    template cannot be changed.

    The `leaders` attribute points to the `Applications` assigned to this
    trip as leaders. The `trippees` attribute contains all the
    `IncomingStudents` who are assigned to the trip.
    """
    objects = TripManager()
    tracker = FieldTracker(fields=[
        'template',
        'section',
        'dropoff_route',
        'pickup_route'])

    template = models.ForeignKey(
        'TripTemplate',
        on_delete=models.PROTECT)

    section = models.ForeignKey(
        'Section',
        on_delete=models.PROTECT,
        related_name='trips')

    notes = models.TextField(blank=True, help_text=(
        "Trip-specific details such as weird timing. "
        "This information will be added to leader packets."
    ))

    # Theses fields override the default transport routes. If any of these
    # routes are set, they are used instead of trip.template.*_route.
    # Is there a way to easily tell when a route is way off for a stop?
    ROUTE_HELP_TEXT = 'leave blank to use default route from template'
    dropoff_route = models.ForeignKey(
        'transport.Route', blank=True, null=True, on_delete=models.PROTECT,
        related_name='overridden_dropped_off_trips', help_text=ROUTE_HELP_TEXT)
    pickup_route = models.ForeignKey(
        'transport.Route', blank=True, null=True, on_delete=models.PROTECT,
        related_name='overridden_picked_up_trips', help_text=ROUTE_HELP_TEXT)
    return_route =  models.ForeignKey(
        'transport.Route', blank=True, null=True, on_delete=models.PROTECT,
        related_name='overriden_returning_trips', help_text=ROUTE_HELP_TEXT)

    class Meta:
        # no two Trips can have the same template-section-trips_year
        # combination; we don't want to schedule two identical trips
        unique_together = ('template', 'section', 'trips_year')
        ordering = ('section__name', 'template__name')

    def clean(self):
        if self.pk is not None:
            if self.tracker.has_changed('section'):
                raise ValidationError("Cannot change a Trip's section.")
            if self.tracker.has_changed('template'):
                raise ValidationError("Cannot change a Trip's template.")

    def get_dropoff_route(self):
        """
        Returns the overriden dropoff, if set
        """
        return self.dropoff_route or self.template.dropoff_stop.route

    def get_pickup_route(self):
        """
        Returns the overriden pickup, if set
        """
        return self.pickup_route or self.template.pickup_stop.route

    def get_return_route(self):
        """
        Returns the overriden return route, if set
        """
        return self.return_route or self.template.return_route

    def get_dropoff_time(self):
        """
        Return the dropoff time, calculated from the Google Maps route.

        Returns None if the bus is not scheduled.
        """
        if self.get_dropoff_stoporder() is None:
            return None
        return self.get_dropoff_stoporder().time

    def get_pickup_time(self):
        """
        Return the pickup time, calculated from the Google Maps route.

        Returns None if the bus is not scheduled.
        """
        if self.get_pickup_stoporder() is None:
            return None
        return self.get_pickup_stoporder().time

    def get_dropoff_bus(self):
        """
        Return the bus that is dropping off this Trip, or None if the bus is
        not scheduled.
        """
        from fyt.transport.models import InternalBus
        return InternalBus.objects.filter(
            route=self.get_dropoff_route(),
            date=self.dropoff_date
        ).first()

    def get_pickup_bus(self):
        """
        Return the bus that is picking up this Trip, or None if the bus is not
        scheduled.
        """
        from fyt.transport.models import InternalBus
        return InternalBus.objects.filter(
            route=self.get_pickup_route(),
            date=self.pickup_date
        ).first()

    def get_dropoff_stoporder(self):
        from fyt.transport.models import StopOrder
        try:
            return self.stoporder_set.get(stop_type=StopOrder.DROPOFF)
        except StopOrder.DoesNotExist:
            return None

    def get_pickup_stoporder(self):
        from fyt.transport.models import StopOrder
        try:
            return self.stoporder_set.get(stop_type=StopOrder.PICKUP)
        except StopOrder.DoesNotExist:
            return None

    @cache_as('_size')
    def size(self):
        """
        Return the number trippees + leaders on this trip

        TODO: use a constant, NUM_TRIPPEES
        """
        if hasattr(self, 'num_trippees') and hasattr(self, 'num_leaders'):
            return self.num_trippees + self.num_leaders
        return self.leaders.count() + self.trippees.count()

    @property
    def dropoff_date(self):
        return self.section.at_campsite1

    @property
    def pickup_date(self):
        return self.section.arrive_at_lodge

    @property
    def return_date(self):
        return self.section.return_to_campus

    @property
    def half_foodbox(self):
        """
        A trip gets an additional half foodbox if it is larger
        than the kickin limit specified by the triptype.
        """
        return self.size() >= self.template.triptype.half_kickin

    @property
    def supp_foodbox(self):
        """
        Does the trip get a supplemental foodbox?
        """
        return self.template.triptype.gets_supplemental

    @property
    def bagels(self):
        """
        How many bagels does to the trip get?
        """
        if self.supp_foodbox:
            num = NUM_BAGELS_SUPPLEMENT
        else:
            num = NUM_BAGELS_REGULAR
        return math.ceil(num * self.size())

    def __str__(self):
        return '{}{}'.format(self.section.name, self.template.name)

    def verbose_str(self):
        return '{}{}: {}'.format(
            self.section.name, self.template.name,
            self.template.description_summary
        )


class Section(DatabaseModel):
    """
    Model to represent a trips section.
    """

    class Meta:
        ordering = ['name']

    name = models.CharField(
        max_length=1, help_text="A, B, C, etc.", verbose_name='Section'
    )
    leaders_arrive = models.DateField()

    is_local = models.BooleanField(default=False)
    is_exchange = models.BooleanField(default=False)
    is_transfer = models.BooleanField(default=False)
    is_international = models.BooleanField(default=False)
    is_fysep = models.BooleanField(default=False)
    is_native = models.BooleanField(default=False)

    objects = SectionManager()
    dates = SectionDatesManager()
    tracker = FieldTracker(fields=['leaders_arrive'])

    @property
    def trippees_arrive(self):
        """
        Date that trippees arrive in Hanover.
        """
        return self.leaders_arrive + timedelta(days=1)

    @property
    def at_campsite1(self):
        """
        Date that section is at first campsite
        """
        return self.leaders_arrive + timedelta(days=2)

    @property
    def at_campsite2(self):
        """
        Date the section is at the second campsite
        """
        return self.leaders_arrive + timedelta(days=3)

    @property
    def nights_camping(self):
        """
        List of dates when trippees are camping out on the trail.
        """
        return [self.at_campsite1, self.at_campsite2]

    @property
    def arrive_at_lodge(self):
        """
        Date section arrives at the lodge.
        """
        return self.leaders_arrive + timedelta(days=4)

    @property
    def return_to_campus(self):
        """
        Date section returns to campus from the lodge
        """
        return self.leaders_arrive + timedelta(days=5)

    @property
    def trip_dates(self):
        """
        All dates when trippees are here for trips.

        Excludes the day leaders arrive.
        """
        return [
            self.trippees_arrive,
            self.at_campsite1,
            self.at_campsite2,
            self.arrive_at_lodge,
            self.return_to_campus]

    @property
    def leader_dates(self):
        """
        All dates when leaders are here for trips.
        """
        return [self.leaders_arrive] + self.trip_dates

    def __str__(self):
        return 'Section ' + self.name

    def leader_date_str(self):
        """
        Return a string of dates that this section covers.

        These are the leader dates.
        Looks like 'Aug 10th to Aug 15th'
        """
        fmt = '%b %d'
        return (self.leaders_arrive.strftime(fmt) + ' to ' +
                self.return_to_campus.strftime(fmt))

    def trippee_date_str(self):
        """
        Date string for *trippees*
        """
        fmt = '%b %d'
        return (self.trippees_arrive.strftime(fmt) + ' to ' +
                self.return_to_campus.strftime(fmt))


def validate_triptemplate_name(value):
    """
    Validator for TripTemplate.name
    """
    if value < 0 or value > 999:
        raise ValidationError('Value must be in range 0-999')


class TripTemplate(DatabaseModel):
    tracker = FieldTracker(fields=['dropoff_stop', 'pickup_stop'])

    name = models.PositiveSmallIntegerField(
        db_index=True, validators=[validate_triptemplate_name]
    )
    description_summary = models.CharField("Summary", max_length=255)

    triptype = models.ForeignKey(
        'TripType', verbose_name='trip type', on_delete=models.PROTECT
    )
    max_trippees = models.PositiveSmallIntegerField()
    swimtest_required = models.BooleanField(
        default=False, help_text=(
            "if selected, available trippees will "
            "be at least 'BEGINNER' swimmers"
        )
    )
    dropoff_stop = models.ForeignKey(
        'transport.Stop', related_name='dropped_off_trips',
        on_delete=models.PROTECT)
    pickup_stop = models.ForeignKey(
        'transport.Stop', related_name='picked_up_trips',
        on_delete=models.PROTECT)
    return_route = models.ForeignKey(
        'transport.Route', related_name='returning_trips',
        on_delete=models.PROTECT)

    # TODO: better related names
    campsite1 = models.ForeignKey(
        'Campsite', related_name='trip_night_1', on_delete=models.PROTECT,
        verbose_name='campsite 1')
    campsite2 = models.ForeignKey(
        'Campsite', related_name='trip_night_2', on_delete=models.PROTECT,
        verbose_name='campsite 2')

    desc_intro = models.TextField('Introduction', blank=True)
    desc_day1 = models.TextField('Day 1', blank=True)
    desc_day2 = models.TextField('Day 2', blank=True)
    desc_day3 = models.TextField('Day 3', blank=True)
    desc_conc = models.TextField('Conclusion', blank=True)
    revisions = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    @property
    def max_num_people(self):
        """
        Maximum number of people on trip: max_trippees + 2 leaders
        """
        return self.max_trippees + 2

    def file_upload_url(self):
        """
        Url used to attach files to this trip template
        """
        return reverse('core:triptemplate:upload_file', kwargs={
            'trips_year': self.trips_year, 'triptemplate_pk': self.pk
        })

    def file_list_url(self):
        """
        Url for list of all attached files
        """
        return reverse('core:triptemplate:document_list', kwargs=self.obj_kwargs())

    def __str__(self):
        return "{}: {}".format(self.name, self.description_summary)


class Document(DatabaseModel):
    """
    A file upload (e.g. a map) that accompanies a TripTemplate.

    Should this be restricted to PDFs? Allow images?
    """
    template = models.ForeignKey(
        'TripTemplate',
        on_delete=models.PROTECT,
        related_name='documents')

    name = models.CharField(max_length=255)
    file = models.FileField()

    def detail_url(self):
        return self.file.url

    def delete_url(self):
        kwargs = self.obj_kwargs()
        kwargs.update({'triptemplate_pk': self.template.pk})
        return reverse('core:triptemplate:document_delete', kwargs=kwargs)

    def __str__(self):
        return self.name


class TripType(DatabaseModel):

    name = models.CharField(max_length=255, db_index=True)
    leader_description = models.TextField()
    trippee_description = models.TextField()

    # TODO: the packing list should be inherited, somehow.
    # can we have some sort of common/base packing list? and add in extras?
    packing_list = models.TextField(blank=True)

    hidden = models.BooleanField(
        'hide this TripType from leader applications and incoming student '
        'registrations', default=False
    )

    # --- foodbox info ----
    half_kickin = models.PositiveSmallIntegerField(
        'minimum # for a half foodbox', default=10
    )
    gets_supplemental = models.BooleanField(
        'gets a supplemental foodbox?', default=False
    )

    objects = TripTypeManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Campsite(DatabaseModel):
    """
    A location where trips camp
    """
    name = models.CharField(
        max_length=255
    )
    capacity = models.PositiveSmallIntegerField(
        null=True
    )
    directions = models.TextField(
        blank=True
    )
    water_source = models.TextField(
        "closest water source", blank=True
    )
    bear_bag = models.BooleanField(
        "bear-bag required?", default=False
    )
    SHELTER_CHOICES = (
        ('TARP', 'tarp'),
        ('SHELTER', 'shelter'),
        ('CABIN', 'cabin')
    )
    shelter = models.CharField(
        "shelter type", max_length=10, choices=SHELTER_CHOICES
    )
    bugout = models.TextField(
        blank=True, help_text="directions for quick help"
    )
    secret = models.TextField(
        blank=True, help_text="door codes and other secret info"
    )

    class Meta:
        ordering = ['name']

    objects = CampsiteManager()

    def __str__(self):
        return self.name
