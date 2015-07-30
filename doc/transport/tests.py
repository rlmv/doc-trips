from datetime import date, timedelta
import unittest
import itertools

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import ProtectedError
from django.db import IntegrityError
from django.core.urlresolvers import reverse
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from doc.test.testcases import TripsYearTestCase, WebTestCase
from doc.transport.models import Stop, Route, ScheduledTransport, ExternalBus, StopOrder
from doc.transport.constants import Hanover, Lodge
from doc.transport import maps
from doc.transport.views import (
    get_internal_route_matrix, get_internal_rider_matrix, Riders,
    get_internal_issues_matrix, NOT_SCHEDULED, EXCEEDS_CAPACITY,
    get_actual_rider_matrix, TransportChecklist
)
from doc.trips.models import Section, Trip
from doc.incoming.models import IncomingStudent
from doc.db.mommy_recipes import trips_year

"""
TODO: rewrite matrix tests to only test _rider_matrix 
"""

stoporder_recipe = Recipe(
    StopOrder,
    trips_year=foreign_key(trips_year),
    stop_type=itertools.cycle([StopOrder.PICKUP, StopOrder.DROPOFF])
)

class TransportModelTestCase(TripsYearTestCase):

    def test_stop_is_protected_on_route_fk_deletion(self):
        trips_year = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=trips_year)
        stop = mommy.make(Stop, route=route, trips_year=trips_year)
        with self.assertRaises(ProtectedError):
            route.delete()


class StopModelTestCase(TripsYearTestCase):

    def test_get_location_with_coords(self):
        trips_year = self.init_trips_year()
        stop = mommy.make(
            Stop, trips_year=trips_year, 
            lat_lng='43.7030,-72.2895', address='address'
        )
        self.assertEqual(stop.location, '43.7030,-72.2895')

    def test_get_location_with_address(self):
        trips_year = self.init_trips_year()
        stop = mommy.make(Stop, trips_year=trips_year, lat_lng='', address='address')
        self.assertEqual(stop.location, 'address')
    
    def test_get_location_with_address(self):
        trips_year = self.init_trips_year()
        stop = mommy.make(Stop, trips_year=trips_year, lat_lng='', address='address')
        self.assertEqual(stop.location, 'address')

    def test_no_lat_lng_or_address_raises_validation_error(self):
        trips_year = self.init_trips_year()
        stop = mommy.prepare(Stop, trips_year=trips_year, lat_lng='', address='')
        with self.assertRaises(ValidationError):
            stop.full_clean()

    def test___str__(self):
        self.assertEqual(str(mommy.prepare(Stop, name='Boston')), 'Boston')
        

class StopManagerTestCase(TripsYearTestCase):

    def test_external(self):
        trips_year = self.init_current_trips_year()
        external_stop = mommy.make(
            Stop, trips_year=trips_year, route__category=Route.EXTERNAL)
        internal_stop = mommy.make(
            Stop, trips_year=trips_year, route__category=Route.INTERNAL)
        self.assertEqual([external_stop], list(Stop.objects.external(trips_year)))


class RouteManagerTestCase(TripsYearTestCase):
    
    def test_external(self):
        trips_year = self.init_current_trips_year()
        external_route = mommy.make(
            Route, category=Route.EXTERNAL, trips_year=trips_year)
        internal_route = mommy.make(
            Route, category=Route.INTERNAL, trips_year=trips_year)
        self.assertQsEqual(Route.objects.external(trips_year), [external_route])

    def test_internal(self):
        trips_year = self.init_current_trips_year()
        external_route = mommy.make(
            Route, category=Route.EXTERNAL, trips_year=trips_year)
        internal_route = mommy.make(
            Route, category=Route.INTERNAL, trips_year=trips_year)
        self.assertQsEqual(Route.objects.internal(trips_year), [internal_route])


class ScheduledTransportManagerTestCase(TripsYearTestCase):
    
    def test_internal(self):

        ty = self.init_current_trips_year()
        external_transport = mommy.make(
            ScheduledTransport, trips_year=ty, route__category=Route.EXTERNAL)
        internal_transport = mommy.make(
            ScheduledTransport, trips_year=ty, route__category=Route.INTERNAL)
        self.assertQsEqual(ScheduledTransport.objects.internal(ty), [internal_transport])
     
   
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
            url = reverse(name, kwargs={'trips_year': trips_year})
            self.app.get(url, user=director)

        
class ScheduledTransportMatrixTestCase(TripsYearTestCase):

    def test_internal_matrix(self):
        trips_year = self.init_trips_year()
        route = mommy.make(
            Route, trips_year=trips_year, category=Route.INTERNAL
        )
        section = mommy.make(
            Section, trips_year=trips_year, 
            leaders_arrive=date(2015, 1, 1)
        )
        transport = mommy.make(
            ScheduledTransport, trips_year=trips_year,
            route=route, date=date(2015, 1, 2)
        )
        target = {
            route: {
                date(2015,1,2): transport, 
                date(2015,1,3): None, 
                date(2015,1,4): None, 
                date(2015,1,5): None, 
                date(2015,1,6): None,
            }
        }
        matrix = get_internal_route_matrix(trips_year)
        self.assertEqual(target, matrix)

    def test_internal_matrix_again(self):
        trips_year = self.init_current_trips_year()
        route1 = mommy.make(Route, trips_year=trips_year, category=Route.INTERNAL)
        route2 = mommy.make(Route, trips_year=trips_year, category=Route.INTERNAL)
        mommy.make(Section, trips_year=trips_year, leaders_arrive=date(2015, 1, 1))
        mommy.make(Section, trips_year=trips_year, leaders_arrive=date(2015, 1, 2))
        transport1 = mommy.make(
            ScheduledTransport, trips_year=trips_year,
            route=route1, date=date(2015, 1, 2))
        transport2 = mommy.make(
            ScheduledTransport, trips_year=trips_year,
            route=route2, date=date(2015, 1, 4))
        target = {
            route1: {
                date(2015,1,2): transport1, 
                date(2015,1,3): None,
                date(2015,1,4): None, 
                date(2015,1,5): None,
                date(2015,1,6): None,
                date(2015,1,7): None
            }, route2: {
                date(2015,1,2): None,
                date(2015,1,3): None,
                date(2015,1,4): transport2, 
                date(2015,1,5): None, 
                date(2015,1,6): None, 
                date(2015,1,7): None
            }
        }
        matrix = get_internal_route_matrix(trips_year)
        self.assertEqual(target, matrix)


class RidersMatrixTestCase(TripsYearTestCase):

    def test_internal_riders_matrix_with_single_trip(self):
        ty = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section = mommy.make(
            Section, trips_year=ty, 
            leaders_arrive=date(2015, 1, 1)
        )
        trip = mommy.make(
            Trip, trips_year=ty, 
            section=section, 
            template__dropoff__route=route, 
            template__pickup__route=route, 
            template__return_route=route
        )
        n = trip.template.max_num_people
        target = {
            route: {
                date(2015,1,2): Riders(0,0,0), 
                date(2015,1,3): Riders(n,0,0), 
                date(2015,1,4): Riders(0,0,0), 
                date(2015,1,5): Riders(0,n,0), 
                date(2015,1,6): Riders(0,0,n),
            }
        }
        self.assertEqual(target, get_internal_rider_matrix(ty))

    def test_internal_riders_matrix_with_multiple_trips(self):
        ty = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
        # trips share dropoff locations and dates
        trip1 = mommy.make(
            Trip, trips_year=ty, 
            section=section, 
            template__dropoff__route=route, 
            template__pickup__route=route, 
            template__return_route=route
        )
        trip2 = mommy.make(
            Trip, trips_year=ty, 
            section=section, 
            template__dropoff__route=route, 
            template__pickup__route=route, 
            template__return_route=route
        )
        n = trip1.template.max_num_people + trip2.template.max_num_people
        target = {
            route: {
                date(2015,1,2): Riders(0,0,0), 
                date(2015,1,3): Riders(n,0,0), 
                date(2015,1,4): Riders(0,0,0), 
                date(2015,1,5): Riders(0,n,0), 
                date(2015,1,6): Riders(0,0,n),
            }
        }
        self.assertEqual(target, get_internal_rider_matrix(ty))

    def test_internal_riders_matrix_with_multiple_trips_overlap(self):
        ty = self.init_current_trips_year()
        route1 = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        route2 = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section1 = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
        section2 = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 2))
        trip1 = mommy.make(
            Trip, trips_year=ty, 
            section=section1, 
            template__dropoff__route=route1, 
            template__pickup__route=route1, 
            template__return_route=route1
        )
        trip2 = mommy.make(
            Trip, trips_year=ty, 
            section=section2, 
            template__dropoff__route=route2, 
            template__pickup__route=route1, 
            template__return_route=route2
        )
        n = trip1.template.max_num_people 
        m = trip2.template.max_num_people
        target = {
            route1: {
                date(2015,1,2): Riders(0,0,0), 
                date(2015,1,3): Riders(n,0,0), 
                date(2015,1,4): Riders(0,0,0), 
                date(2015,1,5): Riders(0,n,0),
                date(2015,1,6): Riders(0,m,n),
                date(2015,1,7): Riders(0,0,0),
            }, 
            route2: {
                date(2015,1,2): Riders(0,0,0), 
                date(2015,1,3): Riders(0,0,0), 
                date(2015,1,4): Riders(m,0,0), 
                date(2015,1,5): Riders(0,0,0), 
                date(2015,1,6): Riders(0,0,0), 
                date(2015,1,7): Riders(0,0,m),
            }
        }
        self.assertEqual(target, get_internal_rider_matrix(ty))

    def test_internal_riders_matrix_with_overriden_routes(self):
        ty = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015,1,1))
        # route is set *directly* on scheduled trip
        trip = mommy.make(
            Trip, trips_year=ty, 
            section=section,
            dropoff_route=route, 
            pickup_route=route, 
            return_route=route
        )
        n = trip.template.max_num_people
        target = {
            route: {
                date(2015,1,2): Riders(0,0,0), 
                date(2015,1,3): Riders(n,0,0), 
                date(2015,1,4): Riders(0,0,0), 
                date(2015,1,5): Riders(0,n,0), 
                date(2015,1,6): Riders(0,0,n)
            }
        }
        self.assertEqual(target, get_internal_rider_matrix(ty))


class ActualRidersMatrixTestCase(TripsYearTestCase):

    def test_basic_matrix(self):
        trips_year = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=trips_year, category=Route.INTERNAL)
        section = mommy.make(Section, trips_year=trips_year, leaders_arrive=date(2015,1,1))
        trip = mommy.make(
            Trip, trips_year=trips_year, 
            section=section,
            template__dropoff__route=route,
            template__pickup__route=route, 
            template__return_route=route
        )
        n = trip.size()
        target = {
            route: {
                date(2015,1,2): Riders(0,0,0), 
                date(2015,1,3): Riders(n,0,0), 
                date(2015,1,4): Riders(0,0,0), 
                date(2015,1,5): Riders(0,n,0),
                date(2015,1,6): Riders(0,0,n),
            }
        }
        self.assertEqual(target, get_actual_rider_matrix(trips_year))

    def test_actual_riders_matrix_with_multiple_trips_overlap(self):
        ty = self.init_current_trips_year()
        route1 = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        route2 = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section1 = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015,1,1))
        section2 = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015,1,2))
        trip1 = mommy.make(
            Trip, trips_year=ty, 
            section=section1,
            template__dropoff__route=route1, 
            template__pickup__route=route1, 
            template__return_route=route1)
        trip2 = mommy.make(
            Trip, trips_year=ty, 
            section=section2,
            template__dropoff__route=route2, 
            template__pickup__route=route1, 
            template__return_route=route2)
        n = trip1.size() 
        m = trip2.size()
        target = {
            route1: {
                date(2015,1,2): Riders(0,0,0), 
                date(2015,1,3): Riders(n,0,0), 
                date(2015,1,4): Riders(0,0,0), 
                date(2015,1,5): Riders(0,n,0), 
                date(2015,1,6): Riders(0,m,n), 
                date(2015,1,7): Riders(0,0,0)
            },
            route2: {
                date(2015,1,2): Riders(0,0,0), 
                date(2015,1,3): Riders(0,0,0), 
                date(2015,1,4): Riders(m,0,0), 
                date(2015,1,5): Riders(0,0,0), 
                date(2015,1,6): Riders(0,0,0), 
                date(2015,1,7): Riders(0,0,m)}
        }
        self.assertEqual(target, get_actual_rider_matrix(ty))


class IssuesMatrixTestCase(TripsYearTestCase):

    def test_unscheduled(self):
        ty = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
        trip = mommy.make(
            Trip, trips_year=ty, 
            section=section, 
            template__dropoff__route=route, 
            template__pickup__route=route, 
            template__return_route=route
        )
        target = {
            route: {
                date(2015,1,2): None, 
                date(2015,1,3): NOT_SCHEDULED, 
                date(2015,1,4): None, 
                date(2015,1,5): NOT_SCHEDULED, 
                date(2015,1,6): NOT_SCHEDULED
            }
        }
        matrix = get_internal_issues_matrix(
            get_internal_route_matrix(ty), 
            get_internal_rider_matrix(ty)
        )
        self.assertEqual(target, matrix)

    def test_exceeds_capacity(self):
        ty = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=ty, category=Route.INTERNAL)
        section = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))

        trip = mommy.make(
            Trip, trips_year=ty, 
            section=section, 
            template__dropoff__route=route, 
            template__pickup__route=route, 
            template__return_route=route, 
            template__max_trippees=route.vehicle.capacity + 1000 # exceeds capacity
        )
        mommy.make(
            ScheduledTransport, trips_year=ty,
            route=route, date=date(2015, 1, 3)
        )
        mommy.make(
            ScheduledTransport, trips_year=ty,
            route=route, date=date(2015, 1, 5)
        )
        target = {
            route: {
                date(2015,1,2): None, 
                date(2015,1,3): EXCEEDS_CAPACITY, 
                date(2015,1,4): None, 
                date(2015,1,5): EXCEEDS_CAPACITY, 
                date(2015,1,6): NOT_SCHEDULED
            }
        }
        matrix = get_internal_issues_matrix(
            get_internal_route_matrix(ty), 
            get_internal_rider_matrix(ty)
        )
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


class TransportViewsTestCase(WebTestCase):

    csrf_checks = False

    def test_create_external_bus_from_matrix(self):
        
        trips_year=self.init_current_trips_year()
        route = mommy.make(Route, trips_year=trips_year, category=Route.EXTERNAL)
        section = mommy.make(Section, trips_year=trips_year, is_local=True)
        
        # Visit matrix page
        url = reverse('db:externalbus_matrix',
                      kwargs={'trips_year': trips_year})
        res = self.app.get(url, user=self.mock_director())
        # click 'add' button for the single entry
        res = res.click(description='<i class="fa fa-plus"></i>')
        # which takes us to the create page, prepopulated w/ data
        res = res.form.submit()
        # and hopefully creates a new tranport
        ExternalBus.objects.get(route=route, section=section)

    def test_schedule_internal_bus_from_matrix(self):
        trips_year = self.init_trips_year()
        route = mommy.make(
            Route, trips_year=trips_year, category=Route.INTERNAL, pk=1)
        section = mommy.make(
            Section, trips_year=trips_year, leaders_arrive=date(2015, 1, 1))
        # visit matrix
        url = reverse('db:scheduledtransport_index',
                      kwargs={'trips_year': trips_year})
        resp = self.app.get(url, user=self.mock_director())
        # click add
        resp = resp.click(linkid="1-2-2015-create-1")
        resp.form.submit()
        ScheduledTransport.objects.get(date=date(2015, 1, 2), route=route)


class InternalTransportModelTestCase(TripsYearTestCase):

    def test_INTERNAL_validation(self):
        trips_year = self.init_trips_year()
        transport = mommy.make(
            ScheduledTransport, trips_year=trips_year,
            route__category=Route.EXTERNAL
        )
        with self.assertRaises(ValidationError):
            transport.full_clean()

    def test_unique_validation(self):
        trips_year = self.init_trips_year()
        transport = mommy.make(
            ScheduledTransport, trips_year=trips_year,
            route__category=Route.INTERNAL
        )
        with self.assertRaises(IntegrityError):
            mommy.make(
                ScheduledTransport, trips_year=trips_year,
                route=transport.route,
                date=transport.date
            )

    def test_get_stops_with_intermediate(self):
        trips_year = self.init_trips_year()
        bus = mommy.make(
            ScheduledTransport, trips_year=trips_year,
            route__category=Route.INTERNAL
        )
        stop1 = mommy.make(
            Stop, trips_year=trips_year, route=bus.route, distance=100
        )
        trip1 = mommy.make(
            Trip, trips_year=trips_year, template__dropoff=stop1,
            section__leaders_arrive=bus.date - timedelta(days=2)
        )
        stop2 = mommy.make(
            Stop, trips_year=trips_year, route=bus.route, distance=1
        )
        trip2 = mommy.make(
            Trip, trips_year=trips_year, template__pickup=stop2,
            section__leaders_arrive=bus.date - timedelta(days=4)
        )
        self.assertEqual(bus.get_stops(),
                         [Hanover(), stop2, stop1, Lodge()])

    def test_trips_are_added_to_stops(self):
        trips_year = self.init_trips_year()
        bus = mommy.make(
            ScheduledTransport, trips_year=trips_year,
            route__category=Route.INTERNAL
        )
        stop = mommy.make(Stop, trips_year=trips_year, route=bus.route)

        trip1 = mommy.make(  # dropping off
            Trip, trips_year=trips_year, template__dropoff=stop,
            section__leaders_arrive=bus.date - timedelta(days=2)
        )
        trip2 = mommy.make(  # picking up
            Trip, trips_year=trips_year, template__pickup=stop,
            section__leaders_arrive=bus.date - timedelta(days=4)
        )
        trip3 = mommy.make(  # returning
            Trip, trips_year=trips_year, template__return_route=bus.route,
            section__leaders_arrive=bus.date - timedelta(days=5)
        )
        # should compress the two StopOrders to a single stop
        (hanover, stop, lodge) = bus.get_stops()
        #  should set these fields:
        self.assertEqual(hanover.trips_dropped_off, [])
        self.assertEqual(hanover.trips_picked_up, [trip1])
        self.assertEqual(stop.trips_dropped_off, [trip1])
        self.assertEqual(stop.trips_picked_up, [trip2])
        self.assertEqual(lodge.trips_dropped_off, [trip2])
        self.assertEqual(lodge.trips_picked_up, [trip3])

    def test_dont_go_to_lodge_if_no_pickups_or_returns(self):
        trips_year = self.init_trips_year()
        bus = mommy.make(
            ScheduledTransport, trips_year=trips_year,
            route__category=Route.INTERNAL
        )
        stop = mommy.make(Stop, trips_year=trips_year, route=bus.route)
        trip1 = mommy.make(  # dropping off
            Trip, trips_year=trips_year, template__dropoff=stop,
            section__leaders_arrive=bus.date - timedelta(days=2)
        )
        stops = bus.get_stops()
        self.assertEqual(stops, [Hanover(), stop])

    def test_go_to_lodge_if_returns(self):
        trips_year = self.init_trips_year()
        bus = mommy.make(
            ScheduledTransport, trips_year=trips_year,
            route__category=Route.INTERNAL
        )
        trip1 = mommy.make(  # returning to campus
            Trip, trips_year=trips_year, template__return_route=bus.route,
            section__leaders_arrive=bus.date - timedelta(days=5)
        )
        self.assertEqual(bus.get_stops(), [Hanover(), Lodge()])

    def test_capacity_still_has_space(self):
        trips_year = self.init_trips_year()
        bus = mommy.make(
            ScheduledTransport, trips_year=trips_year,
            route__category=Route.INTERNAL,
            route__vehicle__capacity=2
        )
        stop = mommy.make(Stop, trips_year=trips_year, route=bus.route)
        trip = mommy.make(
            Trip, trips_year=trips_year, template__dropoff=stop,
            section__leaders_arrive=bus.date - timedelta(days=2)
        )
        mommy.make(IncomingStudent, 2, trips_year=trips_year, trip_assignment=trip)
        self.assertFalse(bus.over_capacity())

    def test_capacity_over(self):
        trips_year = self.init_trips_year()
        bus = mommy.make(
            ScheduledTransport, trips_year=trips_year,
            route__category=Route.INTERNAL,
            route__vehicle__capacity=1
        )
        stop = mommy.make(Stop, trips_year=trips_year, route=bus.route)
        trip = mommy.make(
            Trip, trips_year=trips_year, template__dropoff=stop,
            section__leaders_arrive=bus.date - timedelta(days=2)
        )
        mommy.make(IncomingStudent, 2, trips_year=trips_year, trip_assignment=trip)
        self.assertTrue(bus.over_capacity())

    def test_capacity_complex(self):
        trips_year = self.init_trips_year()
        bus = mommy.make(
            ScheduledTransport, trips_year=trips_year,
            route__category=Route.INTERNAL,
            route__vehicle__capacity=2
        )
        stop1 = mommy.make(Stop, trips_year=trips_year, route=bus.route, distance=1)
        stop2 = mommy.make(Stop, trips_year=trips_year, route=bus.route, distance=2)
        trip1 = mommy.make(
            Trip, trips_year=trips_year, template__dropoff=stop2,
            section__leaders_arrive=bus.date - timedelta(days=2)
        )
        trip2 = mommy.make(
            Trip, trips_year=trips_year, template__pickup=stop1,
            section__leaders_arrive=bus.date - timedelta(days=4)
        )
        mommy.make(IncomingStudent, 2, trips_year=trips_year, trip_assignment=trip1)
        mommy.make(IncomingStudent, 2, trips_year=trips_year, trip_assignment=trip2)

        # Route looks like this:
        # Hanover - pickup trip1
        # stop1 - pickup trip2
        # stop2 - dropoff trip1
        # Lodge - dropoff trip2
        # ...which, since both trips have 2 people, is over capacity.

        self.assertTrue(bus.over_capacity())

    def test_order_stops(self):
        trips_year = self.init_trips_year()
        bus = mommy.make(ScheduledTransport, trips_year=trips_year)
        trip1 = mommy.make(
            Trip, trips_year=trips_year, dropoff_route=bus.route,
            section__leaders_arrive=bus.date - timedelta(days=2)
        )
        trip2 = mommy.make(
            Trip, trips_year=trips_year, dropoff_route=bus.route,
            section__leaders_arrive=bus.date - timedelta(days=2)
        )
        mommy.make(
            StopOrder, trips_year=trips_year, 
            bus=bus, trip=trip1, order=60, 
            stop_type=StopOrder.DROPOFF)
        mommy.make(
            StopOrder, trips_year=trips_year, 
            bus=bus, trip=trip2, order=35, 
            stop_type=StopOrder.DROPOFF)
        self.assertEqual(bus.order_stops(), [trip2.template.dropoff, 
                                             trip1.template.dropoff])

    def test_order_stops_with_missing_ordering(self):
        trips_year = self.init_trips_year()
        bus = mommy.make(ScheduledTransport, trips_year=trips_year)
        trip1 = mommy.make(
            Trip, trips_year=trips_year, dropoff_route=bus.route,
            section__leaders_arrive=bus.date - timedelta(days=2)
        )
        trip2 = mommy.make(
            Trip, trips_year=trips_year, dropoff_route=bus.route,
            section__leaders_arrive=bus.date - timedelta(days=2),
            template__dropoff__distance=30
        )
        order = mommy.make(
            StopOrder, trips_year=trips_year, 
            bus=bus, trip=trip1, order=60)
        self.assertEqual(bus.get_stops()[1:], [trip2.template.dropoff, 
                                                 trip1.template.dropoff])

    def test_order_stops_deletes_extra_ordering(self):
        trips_year = self.init_trips_year()
        bus = mommy.make(ScheduledTransport, trips_year=trips_year)
        order = mommy.make(StopOrder, trips_year=trips_year, bus=bus)
        self.assertEqual(bus.order_stops(), [])
        self.assertQsEqual(StopOrder.objects.all(), [])
  

class StopOrderingTestCase(WebTestCase):

    def test_stop_property(self):
        stop = mommy.make(Stop)
        o = mommy.make(StopOrder, trip__template__dropoff=stop, stop_type=StopOrder.DROPOFF)
        self.assertEqual(o.stop, stop)
        o = mommy.make(StopOrder, trip__template__pickup=stop, stop_type=StopOrder.PICKUP)
        self.assertEqual(o.stop, stop)
    
    def test_stoporder_order_is_automatically_populated(self):
        trips_year = self.init_trips_year()
        order = StopOrder(
            trips_year=trips_year,
            bus=mommy.make(ScheduledTransport, trips_year=trips_year),
            trip=mommy.make(Trip, trips_year=trips_year, template__dropoff__distance=3),
            stop_type=StopOrder.DROPOFF
        )
        order.save()
        self.assertEqual(order.order, 3)

    def test_stoporder_view_creates_missing_objects(self):
        trips_year = self.init_trips_year()
        bus = mommy.make(ScheduledTransport, trips_year=trips_year)
        trip = mommy.make(
            Trip, trips_year=trips_year, dropoff_route=bus.route,
            section__leaders_arrive=bus.date - timedelta(days=2)
        )
        url = reverse('db:scheduledtransport_order', 
                      kwargs={'trips_year': trips_year, 'bus_pk': bus.pk})
        self.app.get(url, user=self.mock_director())
        so = StopOrder.objects.get(
            bus=bus, trip=trip, stop_type=StopOrder.DROPOFF, 
            order=trip.template.dropoff.distance
        )

    def test_default_manager_ordering(self):
        trips_year = self.init_trips_year()
        o1 = mommy.make(StopOrder, order=4)
        o2 = mommy.make(StopOrder, order=1)
        self.assertQsEqual(StopOrder.objects.all(), [o2, o1], ordered=True)

    def test_select_related_stop(self):
        mommy.make(StopOrder)
        with self.assertNumQueries(1):
            [so.stop for so in StopOrder.objects.all()]

    def test_cannot_update_stop_field_in_form(self):
        trips_year = self.init_trips_year()
        trip = mommy.make(Trip, trips_year=trips_year, 
                          dropoff_route=mommy.make(Route, trips_year=trips_year))
        bus = mommy.make(ScheduledTransport, trips_year=trips_year,
                         route=trip.get_dropoff_route(), date=trip.dropoff_date)
        order = mommy.make(StopOrder, trips_year=trips_year, 
                           trip=trip, stop_type=StopOrder.DROPOFF, bus=bus)
        other_trip = mommy.make(Trip, trips_year=trips_year)

        url = reverse('db:scheduledtransport_order', 
                      kwargs={'trips_year': trips_year, 'bus_pk': bus.pk})
        form = self.app.get(url, user=self.mock_director()).form
        form['form-0-trip'] = other_trip.pk
        form.submit()
        
        order = StopOrder.objects.get(pk=order.pk)
        self.assertEqual(order.stop, trip.template.dropoff)
        
        
class ExternalBusModelTestCase(TripsYearTestCase):

    def test_EXTERNAL_validation(self):
        trips_year = self.init_trips_year()
        transport = mommy.make(
            ExternalBus, trips_year=trips_year,
            route__category=Route.INTERNAL
        )
        with self.assertRaises(ValidationError):
            transport.full_clean()

    def test_unique_validation(self):
        trips_year = self.init_trips_year()
        transport = mommy.make(
            ExternalBus, trips_year=trips_year,
            route__category=Route.EXTERNAL
        )
        with self.assertRaises(IntegrityError):
            mommy.make(
                ExternalBus, trips_year=trips_year,
                route=transport.route,
                section=transport.section
            )
                

class MapsTestCases(TripsYearTestCase):

    def test_split_stops_handling(self):
        trips_year = self.init_trips_year()
        orig, waypoints, dest = maps._split_stops([Hanover(), Lodge()])
        self.assertEqual(orig, Hanover().location)
        self.assertEqual(waypoints, [])
        self.assertEqual(dest, Lodge().location)

    def test_directions_handles_more_than_eight_waypoints(self):
        """ Google maps restricts us to 8 waypoints per request """
        trips_year = self.init_trips_year()
        stops = [mommy.make(Stop, trips_year=trips_year, lat_lng=coord) 
                 for coord in (
                         '43.705639,-72.297404',
                         '43.680288,-72.527876',
                         '43.779934,-72.042908',
                         '43.753303,-72.124643',
                         '43.703049,-72.289567',
                         '43.705639,-72.297404',
                         '44.831956,-71.075664',
                         '44.875039,-71.05471',
                         '43.736252,-72.2519',
                         '43.788074,-72.099655',
                         '44.227489,-71.477737')]
        directions = maps.get_directions(stops)
        self.assertEqual(len(stops), len(directions['legs']) + 1)
        for i, leg in enumerate(directions['legs']):
            self.assertEqual(leg['start_stop'], stops[i])
            self.assertEqual(leg['end_stop'], stops[i + 1])

