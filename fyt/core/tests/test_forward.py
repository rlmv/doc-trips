import webtest
from django.db import models
from model_mommy import mommy

from ..forward import Forward, forward
from ..models import TripsYear

from fyt.applications.models import Volunteer as Application
from fyt.croos.models import Croo
from fyt.incoming.models import IncomingStudent, Registration
from fyt.test import FytTestCase
from fyt.timetable.models import Timetable
from fyt.transport.models import Route, Stop, Vehicle
from fyt.trips.models import TripTemplate


def all_field_names(obj):
    return [f.name for f in obj._meta.get_fields()]


class MigrateForwardTestCase(FytTestCase):
    def assertDataEqual(self, obj1, obj2):
        """
        Check that all data on the objects is equal except for
        pk and trips_year.

        TODO: should this check that objects are for different
        trips_years?
        """
        field_names = set(all_field_names(obj1) + all_field_names(obj2))
        field_names.remove('trips_year')
        field_names.remove('id')

        for name in field_names:
            try:
                field1 = obj1._meta.get_field(name)
                field2 = obj2._meta.get_field(name)

                if isinstance(field1, models.ForeignKey) and not name.endswith(
                    '_id'
                ):  # recurse
                    self.assertDataEqual(getattr(obj1, name), getattr(obj2, name))

                if isinstance(field1, models.ManyToManyField):
                    raise Exception(
                        'ManyToManyFields are not currently handled '
                        'by assertDataEqual'
                    )

                self.assertEqual(field1, field2)
            except models.fields.FieldDoesNotExist:  # reverse/related field
                pass

    def setUp(self):
        self.trips_year = self.init_trips_year()
        self.timetable = mommy.make(Timetable)

    def test_make_next_year(self):
        next_year = self.trips_year.make_next_year()
        self.assertFalse(self.trips_year.is_current)
        self.assertTrue(next_year.is_current)
        self.assertEqual(next_year.year, self.trips_year.year + 1)

    def test_make_next_year_fails_if_not_current(self):
        trips_year = mommy.make(TripsYear, is_current=False)
        self.assertRaises(AssertionError, trips_year.make_next_year)

    def test_forward_makes_new_trips_year(self):
        forward()
        prev_year = TripsYear.objects.get(year=self.trips_year.year)
        new_year = TripsYear.objects.get(year=self.trips_year.year + 1)
        self.assertFalse(prev_year.is_current)
        self.assertTrue(new_year.is_current)

    def test_copy_object_with_no_relations_forward(self):
        next_year = self.trips_year.make_next_year()
        # using just as an example
        vehicle = mommy.make(Vehicle, trips_year=self.trips_year)
        new_vehicle = Forward(self.trips_year, next_year).copy_object_forward(vehicle)

        self.assertEqual(new_vehicle.trips_year, next_year)
        self.assertDataEqual(vehicle, new_vehicle)

    def test_copy_object_caches_new_instances(self):
        next_year = self.trips_year.make_next_year()
        vehicle = mommy.make(Vehicle, trips_year=self.trips_year)
        f = Forward(self.trips_year, next_year)

        new_vehicle = f.copy_object_forward(vehicle)
        # copy_object_forward should cache and return same vehicle
        cached_vehicle = f.copy_object_forward(vehicle)

        self.assertEqual(new_vehicle, cached_vehicle)
        self.assertEqual(1, Vehicle.objects.filter(trips_year=next_year).count())

    def test_copy_object_with_fkeys_forward(self):
        next_year = self.trips_year.make_next_year()
        # testing Route, for example
        route = mommy.make(Route, trips_year=self.trips_year)

        f = Forward(self.trips_year, next_year)
        new_route = f.copy_object_forward(route)

        self.assertDataEqual(route, new_route)
        self.assertNotEqual(route.vehicle, new_route.vehicle)

    def test_copy_object_with_null_foreign_key(self):
        next_year = self.trips_year.make_next_year()
        # testing Stop, with nullable Route
        stop = mommy.make(Stop, trips_year=self.trips_year, route=None)
        f = Forward(self.trips_year, next_year)
        new_stop = f.copy_object_forward(stop)
        self.assertIsNone(new_stop.route)

    def test_trippee_med_info_is_deleted(self):
        trippee = mommy.make(
            IncomingStudent, trips_year=self.trips_year, med_info='sparkles'
        )
        registration = mommy.make(
            Registration,
            trips_year=self.trips_year,
            medical_conditions='magic',
            food_allergies='mangoes',
            dietary_restrictions='gluten free',
            needs='dinosaurs',
            epipen=True,
        )
        forward()  # to next year
        trippee.refresh_from_db()
        registration.refresh_from_db()
        self.assertEqual(trippee.med_info, '')
        self.assertEqual(registration.medical_conditions, '')
        self.assertEqual(registration.food_allergies, '')
        self.assertEqual(registration.dietary_restrictions, '')
        self.assertEqual(registration.needs, '')
        self.assertIsNone(registration.epipen)

    def test_application_med_info_is_deleted(self):
        app = mommy.make(
            Application,
            trips_year=self.trips_year,
            medical_conditions='magic',
            food_allergies='mangoes',
            dietary_restrictions='gluten free',
            needs='dinosaurs',
            epipen=True,
        )
        forward()  # to next year
        app.refresh_from_db()
        self.assertEqual(app.medical_conditions, '')
        self.assertEqual(app.food_allergies, '')
        self.assertEqual(app.dietary_restrictions, '')
        self.assertEqual(app.needs, '')
        self.assertIsNone(app.epipen)

    def test_croo_is_migrated(self):
        croo = mommy.make(Croo, trips_year=self.trips_year)
        forward()
        next_croo = Croo.objects.get(trips_year=(self.trips_year.year + 1))
        self.assertDataEqual(next_croo, croo)

    def test_timetable_is_reset(self):
        timetable = Timetable()
        timetable.scoring_available = True
        timetable.hide_volunteer_page = True
        timetable.application_status_available = True
        timetable.leader_assignment_available = True
        timetable.trippee_assignment_available = True
        timetable.save()

        forward()

        timetable = Timetable.objects.timetable()
        self.assertFalse(timetable.scoring_available)
        self.assertFalse(timetable.hide_volunteer_page)
        self.assertFalse(timetable.application_status_available)
        self.assertFalse(timetable.leader_assignment_available)
        self.assertFalse(timetable.trippee_assignment_available)

    def test_complex_hierarchy_is_migrated(self):
        template = mommy.make(
            TripTemplate, trips_year=self.trips_year, description__intro='hello'
        )

        forward()
        new_template = TripTemplate.objects.get(trips_year=self.trips_year.year + 1)

        self.assertTrue(new_template.dropoff_stop.pk is not None)
        self.assertNotEqual(template.dropoff_stop.pk, new_template.dropoff_stop.pk)

        self.assertTrue(new_template.pickup_stop.pk is not None)
        self.assertNotEqual(template.pickup_stop.pk, new_template.pickup_stop.pk)

        self.assertEqual(new_template.description.intro, 'hello')
        self.assertNotEqual(template.description.pk, new_template.description.pk)
