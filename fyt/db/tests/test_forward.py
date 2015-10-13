from django.db import models
from model_mommy import mommy

from ..forward import forward, Forward
from ..models import TripsYear
from fyt.applications.models import GeneralApplication as Application
from fyt.incoming.models import IncomingStudent, Registration
from fyt.test import TripsTestCase
from fyt.transport.models import Route, Vehicle, Stop


class MigrateForwardTestCase(TripsTestCase):

    def assertDataEqual(self, obj1, obj2):
        """
        Check that all data on the objects is equal except for
        pk and trips_year.

        TODO: should this check that objects are for different
        trips_years?
        """
        field_names = set(obj1._meta.get_all_field_names() +
                          obj2._meta.get_all_field_names())
        field_names.remove('trips_year')
        field_names.remove('trips_year_id')
        field_names.remove('id')
       
        for name in field_names:
            try:
                field1 = obj1._meta.get_field(name)
                field2 = obj2._meta.get_field(name)
            
                if isinstance(field1, models.ForeignKey) and not name.endswith('_id'):  # recurse
                    self.assertDataEqual(getattr(obj1, name),
                                         getattr(obj2, name))

                if isinstance(field1, models.ManyToManyField):
                    raise Exception(
                        'ManyToManyFields are not currently handled '
                        'by assertDataEqual')
                
                self.assertEqual(field1, field2)
            except models.fields.FieldDoesNotExist:  # reverse/related field
                pass

    def test_make_next_year(self):
        trips_year = self.init_trips_year()
        next_year = trips_year.make_next_year()
        self.assertFalse(trips_year.is_current)
        self.assertTrue(next_year.is_current)
        self.assertEqual(next_year.year, trips_year.year + 1)

    def test_make_next_year_fails_if_not_current(self):
        trips_year = mommy.make(TripsYear, is_current=False)
        self.assertRaises(AssertionError, trips_year.make_next_year)
  
    def test_forward_makes_new_trips_year(self):
        trips_year = self.init_trips_year()
        forward()
        prev_year = TripsYear.objects.get(year=trips_year.year)
        new_year = TripsYear.objects.get(year=trips_year.year + 1)
        self.assertFalse(prev_year.is_current)
        self.assertTrue(new_year.is_current)

    def test_copy_object_with_no_relations_forward(self):
        trips_year = self.init_trips_year()
        next_year = trips_year.make_next_year()
        # using just as an example
        vehicle = mommy.make(Vehicle, trips_year=trips_year)
        new_vehicle = Forward(
            trips_year, next_year
        ).copy_object_forward(vehicle)
       
        self.assertEqual(new_vehicle.trips_year, next_year)
        self.assertDataEqual(vehicle, new_vehicle)

    def test_copy_object_caches_new_instances(self):
        trips_year = self.init_trips_year()
        next_year = trips_year.make_next_year()
        vehicle = mommy.make(Vehicle, trips_year=trips_year)
        f = Forward(trips_year, next_year)
        
        new_vehicle = f.copy_object_forward(vehicle)
        # copy_object_forward should cache and return same vehicle
        cached_vehicle = f.copy_object_forward(vehicle)
      
        self.assertEqual(new_vehicle, cached_vehicle)
        self.assertEqual(1, Vehicle.objects.filter(trips_year=next_year).count())

    def test_copy_object_with_fkeys_forward(self):
        trips_year = self.init_trips_year()
        next_year = trips_year.make_next_year()
        # testing Route, for example
        route = mommy.make(Route, trips_year=trips_year)
        
        f = Forward(trips_year, next_year)
        new_route = f.copy_object_forward(route)

        self.assertDataEqual(route, new_route)
        self.assertNotEqual(route.vehicle, new_route.vehicle)

    def test_copy_object_with_null_foreign_key(self):
        trips_year = self.init_trips_year()
        next_year = trips_year.make_next_year()
        # testing Stop, with nullable Route
        stop = mommy.make(Stop, trips_year=trips_year, route=None)
        f = Forward(trips_year, next_year)
        new_stop = f.copy_object_forward(stop)
        self.assertIsNone(new_stop.route)

    def test_trippee_med_info_is_deleted(self):
        trips_year = self.init_trips_year()
        trippee = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            med_info='sparkles',
        )
        registration = mommy.make(
            Registration,
            trips_year=trips_year,
            medical_conditions='magic',
            food_allergies='mangoes',
            dietary_restrictions='gluten free',
            needs='dinosaurs',
            epipen=True
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
        trips_year = self.init_trips_year()
        app = mommy.make(
            Application,
            trips_year=trips_year,
            medical_conditions='magic',
            food_allergies='mangoes',
            dietary_restrictions='gluten free',
            needs='dinosaurs',
            epipen=True
        )
        forward()  # to next year
        app.refresh_from_db()
        self.assertEqual(app.medical_conditions, '')
        self.assertEqual(app.food_allergies, '')
        self.assertEqual(app.dietary_restrictions, '')
        self.assertEqual(app.needs, '')
        self.assertIsNone(app.epipen)
