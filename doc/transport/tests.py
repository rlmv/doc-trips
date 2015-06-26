from datetime import date
import unittest

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import ProtectedError
from django.core.urlresolvers import reverse
from model_mommy import mommy

from doc.test.fixtures import TripsYearTestCase, WebTestCase
from doc.transport.models import Stop, Route, ScheduledTransport, ExternalBus
from doc.transport.views import (
    get_internal_route_matrix, get_internal_rider_matrix, Riders, 
    get_internal_issues_matrix, NOT_SCHEDULED, EXCEEDS_CAPACITY,
    get_actual_rider_matrix, TransportChecklist
)
from doc.trips.models import Section, ScheduledTrip
from doc.incoming.models import IncomingStudent

"""
TODO: rewrite matrix tests to only test _rider_matrix 
"""

class TransportModelTestCase(TripsYearTestCase):

    def test_stop_is_protected_on_route_fk_deletion(self):

        trips_year = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=trips_year)
        stop = mommy.make(Stop, route=route, trips_year=trips_year)
        with self.assertRaises(ProtectedError):
            route.delete()


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

    def test_internal_riders_matrix_with_single_trip(self):
        ty = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
      
        trip = mommy.make(ScheduledTrip, trips_year=ty, section=section, template__dropoff__route=route, template__pickup__route=route, template__return_route=route)

        num = trip.template.max_num_people
        target = {route: {date(2015,1,2): Riders(0,0,0), date(2015,1,3): Riders(num,0,0), date(2015, 1,4): Riders(0,0,0), date(2015,1,5): Riders(0,num,0), date(2015,1,6): Riders(0,0,num)}}
        matrix = get_internal_rider_matrix(ty)
        self.assertEqual(target, matrix)

    def test_internal_riders_matrix_with_multiple_trips(self):
        ty = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
        # trips share dropoff locations and dates
        trip1 = mommy.make(ScheduledTrip, trips_year=ty, section=section, template__dropoff__route=route, template__pickup__route=route, template__return_route=route)
        trip2 = mommy.make(ScheduledTrip, trips_year=ty, section=section, template__dropoff__route=route, template__pickup__route=route, template__return_route=route)
        num = trip1.template.max_num_people + trip2.template.max_num_people
        target = {route: {date(2015,1,2): Riders(0,0,0), date(2015,1,3): Riders(num,0,0), date(2015, 1,4): Riders(0,0,0), date(2015,1,5): Riders(0,num,0), date(2015,1,6): Riders(0,0,num)}}
        matrix = get_internal_rider_matrix(ty)
        self.assertEqual(target, matrix)

    def test_internal_riders_matrix_with_multiple_trips_overlap(self):
        ty = self.init_current_trips_year()
        route1 = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        route2 = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section1 = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
        section2 = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 2))
        trip1 = mommy.make(ScheduledTrip, trips_year=ty, section=section1, template__dropoff__route=route1, template__pickup__route=route1, template__return_route=route1)
        trip2 = mommy.make(ScheduledTrip, trips_year=ty, section=section2, template__dropoff__route=route2, template__pickup__route=route1, template__return_route=route2)
        n1 = trip1.template.max_num_people 
        n2 = trip2.template.max_num_people
        target = {
            route1: {date(2015,1,2): Riders(0,0,0), date(2015,1,3): Riders(n1,0,0), date(2015,1,4): Riders(0,0,0), date(2015,1,5): Riders(0,n1,0), date(2015,1,6): Riders(0,n2,n1), date(2015,1,7): Riders(0,0,0)},
            route2: {date(2015,1,2): Riders(0,0,0), date(2015,1,3): Riders(0,0,0), date(2015,1,4): Riders(n2,0,0), date(2015,1,5): Riders(0,0,0), date(2015,1,6): Riders(0,0,0), date(2015,1,7): Riders(0,0,n2)}
        }
        matrix = get_internal_rider_matrix(ty)

        self.assertEqual(target, matrix)

    def test_internal_riders_matrix_with_overriden_routes(self):
        ty = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
        # route is set *directly* on scheduled trip
        trip = mommy.make(ScheduledTrip, trips_year=ty, section=section,
                          dropoff_route=route, pickup_route=route, return_route=route)
        num = trip.template.max_num_people
        target = {route: {date(2015,1,2): Riders(0,0,0), date(2015,1,3): Riders(num,0,0), date(2015, 1,4): Riders(0,0,0), date(2015,1,5): Riders(0,num,0), date(2015,1,6): Riders(0,0,num)}}
        matrix = get_internal_rider_matrix(ty)
        self.assertEqual(target, matrix)


class ActualRidersMatrixTestCase(TripsYearTestCase):

    def test_basic_matrix(self):
        trips_year = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=trips_year, category=Route.INTERNAL)
        section = mommy.make(Section, trips_year=trips_year, leaders_arrive=date(2015, 1, 1))
        trip = mommy.make(ScheduledTrip, trips_year=trips_year, section=section, template__dropoff__route=route, template__pickup__route=route, template__return_route=route)
        num = trip.size()
        target = {route: {date(2015,1,2): Riders(0,0,0), date(2015,1,3): Riders(num,0,0), date(2015, 1,4): Riders(0,0,0), date(2015,1,5): Riders(0,num,0), date(2015,1,6): Riders(0,0,num)}}
        matrix = get_actual_rider_matrix(trips_year)
        self.assertEqual(target, matrix)

    def test_actual_riders_matrix_with_multiple_trips_overlap(self):
        ty = self.init_current_trips_year()
        route1 = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        route2 = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section1 = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
        section2 = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 2))
        trip1 = mommy.make(ScheduledTrip, trips_year=ty, section=section1, template__dropoff__route=route1, template__pickup__route=route1, template__return_route=route1)
        trip2 = mommy.make(ScheduledTrip, trips_year=ty, section=section2, template__dropoff__route=route2, template__pickup__route=route1, template__return_route=route2)
        n1 = trip1.size() 
        n2 = trip2.size()
        target = {
            route1: {date(2015,1,2): Riders(0,0,0), date(2015,1,3): Riders(n1,0,0), date(2015,1,4): Riders(0,0,0), date(2015,1,5): Riders(0,n1,0), date(2015,1,6): Riders(0,n2,n1), date(2015,1,7): Riders(0,0,0)},
            route2: {date(2015,1,2): Riders(0,0,0), date(2015,1,3): Riders(0,0,0), date(2015,1,4): Riders(n2,0,0), date(2015,1,5): Riders(0,0,0), date(2015,1,6): Riders(0,0,0), date(2015,1,7): Riders(0,0,n2)}
        }
        matrix = get_actual_rider_matrix(ty)

        self.assertEqual(target, matrix)


class IssuesMatrixTestCase(TripsYearTestCase):

    def test_unscheduled(self):
        ty = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
        trip = mommy.make(ScheduledTrip, trips_year=ty, section=section, template__dropoff__route=route, template__pickup__route=route, template__return_route=route)

        target = {route: {date(2015,1,2): None, date(2015,1,3): NOT_SCHEDULED, date(2015,1,4): None, date(2015,1,5): NOT_SCHEDULED, date(2015,1,6): NOT_SCHEDULED}}
        matrix = get_internal_issues_matrix(get_internal_route_matrix(ty), get_internal_rider_matrix(ty))
        self.assertEqual(target, matrix)

    def test_exceeds_capacity(self):
        ty = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))

        max_trippees = route.vehicle.capacity + 1000 # exceed capacity
        trip = mommy.make(ScheduledTrip, trips_year=ty, section=section, template__dropoff__route=route, template__pickup__route=route, template__return_route=route, template__max_trippees=max_trippees)

        mommy.make(ScheduledTransport, trips_year=ty,route=route, date=date(2015, 1, 3))
        mommy.make(ScheduledTransport, trips_year=ty,route=route, date=date(2015, 1, 5))
           
        target = {route: {date(2015,1,2): None, date(2015,1,3): EXCEEDS_CAPACITY, date(2015,1,4): None, date(2015,1,5): EXCEEDS_CAPACITY, date(2015,1,6): NOT_SCHEDULED}}
        matrix = get_internal_issues_matrix(get_internal_route_matrix(ty), get_internal_rider_matrix(ty))
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


class TransportChecklistTest(TripsYearTestCase):
    
    def test_get_date(self):
        view = TransportChecklist()
        d = date(2015, 1, 1)
        view.kwargs = {'date': str(d)}
        self.assertEqual(view.get_date(), d)


class ExternalBusManager(TripsYearTestCase):

    def test_schedule_matrix(self):
        trips_year = self.init_current_trips_year()
        
        sxn1 = mommy.make(Section, trips_year=trips_year, is_local=True)
        sxn2 = mommy.make(Section, trips_year=trips_year, is_local=True)
        not_local_sxn = mommy.make(Section, trips_year=trips_year, is_local=False)
        
        route1 = mommy.make(Route, trips_year=trips_year, category=Route.EXTERNAL)
        route2 = mommy.make(Route, trips_year=trips_year, category=Route.EXTERNAL)
        internal = mommy.make(Route, trips_year=trips_year, category=Route.INTERNAL)

        transp1 = mommy.make(ExternalBus, trips_year=trips_year, 
                                route=route1, section=sxn2)
        transp2 = mommy.make(ExternalBus, trips_year=trips_year, 
                                route=route2, section=sxn1)

        matrix = ExternalBus.objects.schedule_matrix(trips_year)
        target = {
            route1: {sxn1: None, sxn2: transp1},
            route2: {sxn1: transp2, sxn2: None},
        }
        self.assertEqual(matrix, target)

    def test_simple_passengers_matrix(self):
        trips_year = self.init_trips_year()
        sxn = mommy.make(Section, trips_year=trips_year, is_local=True)
        rt = mommy.make(Route, trips_year=trips_year, category=Route.EXTERNAL)
        passenger = mommy.make(
            IncomingStudent, trips_year=trips_year,
            bus_assignment__route=rt,
            trip_assignment__section=sxn
        )
        target = {rt: {sxn: 1}}
        actual = ExternalBus.passengers.matrix(trips_year)
        
        self.assertEqual(target, actual)

    def test_passengers_matrix_with_multiples(self):
        trips_year = self.init_trips_year()
        sxn1 = mommy.make(Section, trips_year=trips_year, is_local=True)
        sxn2 = mommy.make(Section, trips_year=trips_year, is_local=True)
        rt1 = mommy.make(Route, trips_year=trips_year, category=Route.EXTERNAL)
        psgr1 = mommy.make(
            IncomingStudent, trips_year=trips_year,
            bus_assignment__route=rt1,
            trip_assignment__section=sxn1
        )
        psgr2 = mommy.make(
            IncomingStudent, trips_year=trips_year,
            bus_assignment__route=rt1,
            trip_assignment__section=sxn1
        )
        psgr3 = mommy.make(
            IncomingStudent, trips_year=trips_year,
            bus_assignment__route=rt1,
            trip_assignment__section=sxn2,
        )
        not_psgr1 = mommy.make(
            IncomingStudent, trips_year=trips_year,
            bus_assignment__route=rt1
        )
        not_psgr2 = mommy.make(
            IncomingStudent, trips_year=trips_year,
            trip_assignment__section=sxn2
        )
        target = {rt1: {sxn1: 2, sxn2: 1}}
        actual = ExternalBus.passengers.matrix(trips_year)
        self.assertEqual(target, actual)


class ExternalBusView(WebTestCase):

    csrf_checks = False

    def test_create_from_matrix(self):
        
        trips_year=self.init_current_trips_year()
        route = mommy.make(Route, trips_year=trips_year, category=Route.EXTERNAL)
        section = mommy.make(Section, trips_year=trips_year, is_local=True)
        
        # Visit matrix page
        url = reverse('db:externalbus_matrix',
                      kwargs={'trips_year': trips_year})
        res = self.app.get(url, user=self.mock_director())
        # click 'add' button for the single entry
        res = res.click(description='add')
        # which takes us to the create page, prepopulated w/ data
        res = res.form.submit()
        # and hopefully creates a new tranport
        ExternalBus.objects.get(route=route, section=section)
