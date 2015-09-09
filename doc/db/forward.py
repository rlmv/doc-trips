import copy
from django.db import models
from django.db.transaction import atomic

from .models import TripsYear
from doc.applications.models import ApplicationInfo, PortalContent
from doc.incoming.models import Settings
from doc.raids.models import RaidInfo
from doc.transport.models import Vehicle, Route, Stop
from doc.trips.models import TripTemplate, TripType, Campsite

"""
Migrate the database to the next ``trips_year``
"""

MODELS_FORWARD = [
    ApplicationInfo,
    PortalContent,
    Settings,
    RaidInfo,
    Stop,
    Route,
    Vehicle,
    TripTemplate,
    TripType,
    Campsite
]


class Forward():

    def __init__(self, curr_year, next_year):
        self.curr_year = curr_year
        self.next_year = next_year
        #: cache for objects which have already been migrated
        self.old_to_new = {}

    def do(self):
        """
        Migrate all models
        """
        for Model in MODELS_FORWARD:
            for obj in Model.objects.filter(trips_year=self.curr_year):
                self.copy_object_forward(obj)

    def copy_object_forward(self, obj):
        """
        Recursively make a copy of ``obj`` for the next ``trips_year``

        Caches all new objects in ``self.old_to_new`` so that if we
        encounter a previously created object we return the cached copy.

        Returns the new object.
        """
        try:  # cached?
            return self.old_to_new[obj]
        except KeyError:
            pass

        new_obj = copy.copy(obj)

        # recursively copy foreign keys
        for name in obj._meta.get_all_field_names():
            try:
                field = obj._meta.get_field(name)
            except models.fields.FieldDoesNotExist:  # reverse/related field
                continue

            if isinstance(field, models.ForeignKey) and (
                    field.related_field.model != TripsYear):
                rel = self.copy_object_forward(getattr(obj, name))
                setattr(new_obj, name, rel)

            if isinstance(field, models.ManyToManyField):
                raise Exception(
                    'ManyToManyFields are not currently handled '
                    'by copy_object_forward')

        new_obj.trips_year = self.next_year
        new_obj.pk = None
        new_obj.save()

        self.old_to_new[obj] = new_obj
        return new_obj


@atomic
def forward():
    """
    Copy over all persisting objects, delete sensitive info, etc.

    This action is not reversible.
    """
    curr_year = TripsYear.objects.current()
    next_year = curr_year.make_next_year()
    # bye bye!
    Forward(curr_year, next_year).do()
