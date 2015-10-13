import copy
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.transaction import atomic

from .models import TripsYear
from fyt.applications.models import ApplicationInformation, PortalContent, GeneralApplication as Application
from fyt.incoming.models import Settings, IncomingStudent, Registration
from fyt.raids.models import RaidInfo
from fyt.transport.models import Vehicle, Route, Stop
from fyt.trips.models import TripTemplate, TripType, Campsite

"""
Migrate the database to the next ``trips_year``
"""

logger = logging.getLogger(__name__)

#: all models which need to be migrated
MODELS_FORWARD = [
    ApplicationInformation,
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
    """
    """
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

        self.delete_trippee_medical_info()
        self.delete_application_medical_info()

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
            
        logger.info('Copying %s' % obj)
        new_obj = copy.copy(obj)

        # recursively copy foreign keys
        for field in obj._meta.get_fields():
            if isinstance(field, models.ForeignKey) and field.related_model != TripsYear:
                if getattr(obj, field.name) is not None:
                    new_rel = self.copy_object_forward(getattr(obj, field.name))
                else:
                    new_rel = None
                setattr(new_obj, field.name, new_rel)

            if field.many_to_many:
                raise Exception(
                    'ManyToManyFields are not currently handled '
                    'by copy_object_forward')

        new_obj.trips_year = self.next_year
        new_obj.pk = None
        new_obj.save()

        self.old_to_new[obj] = new_obj
        return new_obj

    def delete_trippee_medical_info(self):
        """
        Delete all medical info saved on
        ``IncomingStudents`` and ``Registrations``.
        """
        for inc in IncomingStudent.objects.filter(trips_year=self.curr_year):
            inc.med_info = ''
            inc.save()

        for reg in Registration.objects.filter(trips_year=self.curr_year):
            reg.delete_medical_info()

    def delete_application_medical_info(self):
        """
        Delete all medical info saved on ``GeneralApplications``
        """
        for app in Application.objects.filter(trips_year=self.curr_year):
            app.delete_medical_info()


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
