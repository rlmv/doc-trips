from datetime import date
import unittest

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import ProtectedError
from django.core.urlresolvers import reverse
from model_mommy import mommy

from doc.test.fixtures import TripsYearTestCase, WebTestCase
from doc.transport.models import Stop, Route, ScheduledTransport
from doc.transport.views import get_internal_route_matrix, get_internal_rider_matrix, Riders
from doc.trips.models import Section, ScheduledTrip


class TransportModelTestCase(TripsYearTestCase):

    def test_stop_is_protected_on_route_fk_deletion(self):

        trips_year = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=trips_year)
        stop = mommy.make(Stop, route=route, trips_year=trips_year)
        with self.assertRaises(ProtectedError):
            route.delete()


class ScheduledTransportModelTestCase(TripsYearTestCase):

    def test_date_and_section_raise_error(self):
        trips_year = self.init_current_trips_year()
        t = mommy.make(ScheduledTransport, trips_year=trips_year,
                       date=timezone.now(),
                       section=mommy.make(Section, trips_year=trips_year))
        with self.assertRaises(ValidationError):
            t.full_clean()

    def test_no_date_and_no_section_raises_error(self):
        trips_year = self.init_current_trips_year()
        t = mommy.make(ScheduledTransport, trips_year=trips_year,
                       date=None, section=None)
        with self.assertRaises(ValidationError):
            t.full_clean()

    def test_validation_error_with_INTERNAL_and_section(self):
        trips_year = self.init_current_trips_year()
        t = mommy.make(ScheduledTransport, trips_year=trips_year,
                       route__category=Route.INTERNAL, date=None,
                       section=mommy.make(Section, trips_year=trips_year), )
        with self.assertRaises(ValidationError):
            t.full_clean()

    def test_validation_error_with_EXTERNAL_and_date(self):
        trips_year = self.init_current_trips_year()
        t = mommy.make(ScheduledTransport, trips_year=trips_year,
                       route__category=Route.EXTERNAL,
                       date=timezone.now(), section=None)
        with self.assertRaises(ValidationError):
            t.full_clean()


class StopManagerTestCase(TripsYearTestCase):

    def test_external(self):
        
        trips_year = self.init_current_trips_year()
        external_stop = mommy.make(Stop, trips_year=trips_year, route__category=Route.EXTERNAL)
        internal_stop = mommy.make(Stop, trips_year=trips_year, route__category=Route.INTERNAL)
        self.assertEqual([external_stop], list(Stop.objects.external(trips_year)))


class RouteManagerTestCase(TripsYearTestCase):
    
    def test_external(self):
        trips_year = self.init_current_trips_year()
        external_route = mommy.make(Route, category=Route.EXTERNAL, trips_year=trips_year)
        internal_route = mommy.make(Route, category=Route.INTERNAL, trips_year=trips_year)
        self.assertEqual([external_route], list(Route.objects.external(trips_year)))

    def test_internal(self):
        trips_year = self.init_current_trips_year()
        external_route = mommy.make(Route, category=Route.EXTERNAL, trips_year=trips_year)
        internal_route = mommy.make(Route, category=Route.INTERNAL, trips_year=trips_year)
        self.assertEqual([internal_route], list(Route.objects.internal(trips_year)))


class ScheduledTransportManagerTestCase(TripsYearTestCase):
    
    def test_internal(self):

        ty = self.init_current_trips_year()
        external_transport = mommy.make(ScheduledTransport, trips_year=ty, route__category=Route.EXTERNAL)
        internal_transport = mommy.make(ScheduledTransport, trips_year=ty, route__category=Route.INTERNAL)
        self.assertEqual([internal_transport], list(ScheduledTransport.objects.internal(ty)))
     
   
class TestViews(WebTestCase):

    def test_index_views(self):
        
        trips_year = self.init_current_trips_year()
        director = self.mock_director()
        
        names = [
            'db:stop_index',
            'db:route_index',
            'db:vehicle_index',
        ]

        for name in names:
            res = self.app.get(reverse(name, kwargs={'trips_year': trips_year}), user=director)

        
class ScheduledTransportMatrixTestCase(TripsYearTestCase):

    def test_internal_matrix(self):
        ty = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
        transport = mommy.make(ScheduledTransport, trips_year=ty,
                               route=route, date=date(2015, 1, 2))

        target = {route: {date(2015,1,2): transport, date(2015,1,3): None, date(2015, 1,4): None, date(2015,1,5): None, date(2015,1,6):None}}
        matrix = get_internal_route_matrix(ty)
        self.assertEqual(target, matrix)

    def test_internal_matrix_again(self):
        ty = self.init_current_trips_year()
        route1 = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        route2 = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
        mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 2))
        transport1 = mommy.make(ScheduledTransport, trips_year=ty,
                               route=route1, date=date(2015, 1, 2))
        transport2 = mommy.make(ScheduledTransport, trips_year=ty,
                                route=route2, date=date(2015, 1, 4))
        target = {route1: {date(2015,1,2): transport1, date(2015,1,3): None, date(2015, 1,4): None, date(2015,1,5): None, date(2015,1,6):None, date(2015,1,7):None},
                  route2: {date(2015,1,2): None, date(2015,1,3): None, date(2015, 1,4): transport2, date(2015,1,5): None, date(2015,1,6):None, date(2015,1,7):None}}
        matrix = get_internal_route_matrix(ty)
        self.assertEqual(target, matrix)


class RidersMatrixTestCase(TripsYearTestCase):

    def test_internal_riders_matrix(self):
        ty = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
      
        trip = mommy.make(ScheduledTrip, trips_year=ty, section=section, template__dropoff__route=route, template__pickup__route=route, template__return_route=route)

        num = trip.template.max_num_people
        target = {route: {date(2015,1,2): Riders(0,0,0), date(2015,1,3): Riders(num,0,0), date(2015, 1,4): Riders(0,0,0), date(2015,1,5): Riders(0,num,0), date(2015,1,6): Riders(0,0,num)}}
        matrix = get_internal_rider_matrix(ty)
        self.assertEqual(target, matrix)
        
    
class RidersClassTestCase(unittest.TestCase):

    def test__add__(self):
        r1 = Riders(0, 0, 1)
        r2 = Riders(1, 1, 1)
        new = r1 + r2
        self.assertEqual(new.dropping_off, 1)
        self.assertEqual(new.picking_up, 1)
        self.assertEqual(new.returning, 2)

    def test__bool__true(self):
        self.assertTrue(Riders(0, 0, 1))
        self.assertTrue(Riders(0, 2, 0))
        self.assertTrue(Riders(2012, 0, 0))

    def test__bool__false(self):
        r1 = Riders(0, 0, 0)
        self.assertFalse(r1)

    def test__eq__(self):
        self.assertEqual(Riders(0,0,0), Riders(0,0,0))
        self.assertNotEqual(Riders(1,2,3), Riders(0,0,0))
    
