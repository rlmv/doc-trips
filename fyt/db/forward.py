import copy
import logging

from bulk_update.helper import bulk_update as _bulk_update
from django.conf import settings
from django.db.transaction import atomic

from .models import TripsYear

from fyt.applications.models import (
    ApplicationInformation,
    PortalContent,
    Question,
    Volunteer as Application,
)
from fyt.croos.models import Croo
from fyt.incoming.models import IncomingStudent, Registration, Settings
from fyt.raids.models import RaidInfo
from fyt.timetable.models import Timetable
from fyt.training.models import Training
from fyt.transport.models import Route, Stop, Vehicle, TransportConfig
from fyt.trips.models import Campsite, Document, TripTemplate, TripType


logger = logging.getLogger(__name__)

# Sqlite databases have a max number of variables in any given query.
# This keeps ``bulk_update`` from causing errors on development
# sqlite databases, but also keeps the site from timing out in
# production.
if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    SQLITE_BATCH_LIMIT = 1
else:
    SQLITE_BATCH_LIMIT = None


def bulk_update(qs):
    _bulk_update(qs, batch_size=SQLITE_BATCH_LIMIT)


class Forward:
    """
    Manages the state of the database migration to the next ``trips_year``.
    """

    #: all models which need to be migrated
    MODELS_FORWARD = [
        ApplicationInformation,
        Question,
        PortalContent,
        Settings,
        RaidInfo,
        Stop,
        Route,
        Vehicle,
        TransportConfig,
        TripTemplate,
        Document,
        TripType,
        Campsite,
        Croo,
        Training,
    ]

    def __init__(self, curr_year, next_year):
        self.curr_year = curr_year
        self.next_year = next_year
        #: cache for objects which have already been migrated
        self.old_to_new = {}

    def do(self):
        """
        Werrrk. Migrate all models listed in ``MODELS_FORWARD``
        """
        for Model in self.MODELS_FORWARD:
            for obj in Model.objects.filter(trips_year=self.curr_year):
                self.copy_object_forward(obj)

        self.delete_trippee_medical_info()
        self.delete_application_medical_info()
        self.reset_timetable()

    def copy_object_forward(self, obj):
        """
        Recursively copy ``obj`` to the next ``trips_year``

        Caches all new objects in ``self.old_to_new`` so that if we
        encounter a previously created object we return the cached copy.

        Returns the new object.
        """
        try:  # cached?
            return self.old_to_new[obj]
        except KeyError:
            pass

        logger.info('Copying %s' % obj)

        # Instantiate a new object.
        # This queries the database instead of using copy() because
        # model_utils.FieldTracker replaces the save() method of tracked
        # models with a function that contains a bound instance of the
        # original object - hence, any save calls to the new object save
        # the original instead.
        new_obj = obj._meta.model.objects.get(pk=obj.pk)

        # recursively copy foreign keys
        for field in obj._meta.get_fields():

            if field.many_to_one and field.related_model != TripsYear:
                rel = getattr(obj, field.name)
                if rel is None:
                    new_rel = None
                else:
                    new_rel = self.copy_object_forward(rel)
                setattr(new_obj, field.name, new_rel)
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
        incoming = IncomingStudent.objects.filter(trips_year=self.curr_year)
        for inc in incoming:
            inc.med_info = ''

        registrations = Registration.objects.filter(trips_year=self.curr_year)
        for reg in registrations:
            reg.clear_medical_info()

        bulk_update(incoming)
        bulk_update(registrations)

    def delete_application_medical_info(self):
        """
        Delete all medical info saved on ``Volunteers``
        """
        applications = Application.objects.filter(trips_year=self.curr_year)
        for app in applications:
            app.clear_medical_info()

        bulk_update(applications)

    def reset_timetable(self):
        """
        Reset the timetable.
        """
        Timetable.objects.timetable().reset()


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
