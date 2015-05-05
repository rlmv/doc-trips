import unittest
from datetime import date, timedelta
from django.db import transaction
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from model_mommy import mommy

from doc.trips.models import ScheduledTrip, Section, TripTemplate, validate_triptemplate_name
from doc.transport.models import Route
from doc.db.urlhelpers import reverse_create_url, reverse_update_url
from doc.test.fixtures import WebTestCase, TripsYearTestCase as TripsTestCase
from doc.applications.tests import make_application
from doc.applications.models import GeneralApplication
from doc.incoming.models import IncomingStudent

class ScheduledTripTestCase(WebTestCase):
    
    csrf_checks = False

    def setUp(self):
        self.init_current_trips_year()

    def test_unique_validation_in_create_view(self):
        """ See the comment in DatabaseMixin.form_valid """
        self.mock_director()

        trip = mommy.make(ScheduledTrip, trips_year=self.trips_year, 
                        template__trips_year=self.trips_year,
                        section__trips_year=self.trips_year)
        trip.save()

        #Posting will raise an IntegrityError if validation is not handled
        response = self.app.post(reverse_create_url(ScheduledTrip, self.trips_year), 
                                 {'template': trip.template.pk, 
                                  'section': trip.section.pk}, 
                                 user=self.director.netid)
        # should have unique constraint error
        self.assertIn('unique constraint failed', str(response.content).lower())
        # should not create the trip
        scheduled_trips = ScheduledTrip.objects.all()
        self.assertEquals(len(scheduled_trips), 1)
        self.assertEquals(scheduled_trips[0], trip)

    def test_num_queries_in_scheduled_trip_matrix(self):
        trips_year = self.trips_year
        template1 = mommy.make(TripTemplate, trips_year=trips_year)
        section1 = mommy.make(Section, trips_year=trips_year)
        template2 = mommy.make(TripTemplate, trips_year=trips_year)
        section2 = mommy.make(Section, trips_year=trips_year)
        mommy.make(ScheduledTrip, section=section1,
                   template=template1, trips_year=trips_year)
        mommy.make(ScheduledTrip, section=section1,
                   template=template2, trips_year=trips_year)
        mommy.make(ScheduledTrip, section=section2,
                   template=template2, trips_year=trips_year)
        user = self.mock_director()
        with self.assertNumQueries(18):
            self.app.get(reverse('db:scheduledtrip_index', kwargs={'trips_year': self.trips_year}), user=user)


class ScheduledTripRouteOverridesTestCase(WebTestCase):

    def test_override_routes_in_trip_update_form(self):
        trips_year = self.init_current_trips_year()
        template = mommy.make(TripTemplate, trips_year=trips_year)
        section = mommy.make(Section, trips_year=trips_year)
        trip = mommy.make(ScheduledTrip, trips_year=trips_year,
                          section=section, template=template)
        route = mommy.make(Route, trips_year=trips_year)
        res = self.app.get(reverse_update_url(trip), user=self.mock_director())
        form = res.form
        form['dropoff_route'] = route.pk
        form['pickup_route'] = route.pk
        form['return_route'] = route.pk
        res = form.submit()
        trip = ScheduledTrip.objects.get(pk=trip.pk)
        self.assertEqual(trip.dropoff_route, route)
        self.assertEqual(trip.pickup_route, route)
        self.assertEqual(trip.return_route, route)

    def test_get_dropoff_route_method(self):
        trips_year = self.init_current_trips_year()
        trip = mommy.make(ScheduledTrip, trips_year=trips_year, 
                          template__dropoff__route=mommy.make(Route, trips_year=trips_year))
        self.assertEqual(trip.get_dropoff_route(), trip.template.dropoff.route)
        # override default route
        trip.dropoff_route = mommy.make(Route, trips_year=trips_year)
        trip.save()
        self.assertEqual(trip.get_dropoff_route(), trip.dropoff_route)

    def test_get_pickup_route_method(self):
        trips_year = self.init_current_trips_year()
        trip = mommy.make(ScheduledTrip, trips_year=trips_year)

        self.assertEqual(trip.get_pickup_route(), trip.template.pickup.route)
        # override default route
        trip.pickup_route = mommy.make(Route, trips_year=trips_year)
        trip.save()
        self.assertEqual(trip.get_pickup_route(), trip.pickup_route)

    def test_get_return_route_method(self):
        trips_year = self.init_current_trips_year()
        trip = mommy.make(ScheduledTrip, trips_year=trips_year)
        self.assertEqual(trip.get_return_route(), trip.template.return_route)
        # override default route
        trip.return_route = mommy.make(Route, trips_year=trips_year)
        trip.save()
        self.assertEqual(trip.get_return_route(), trip.return_route)

    def test_size_method_with_noone(self):
        trips_year = self.init_current_trips_year()
        trip = mommy.make(ScheduledTrip, trips_year=trips_year)
        self.assertEqual(trip.size(), 0)

    def test_size_method_with_1_leader(self):
        trips_year = self.init_current_trips_year()
        trip = mommy.make(ScheduledTrip, trips_year=trips_year)
        make_application(trips_year=trips_year, assigned_trip=trip)
        self.assertEqual(trip.size(), 1)

    def test_size_method_with_1_leader_and_2_trippees(self):
        trips_year = self.init_current_trips_year()
        trip = mommy.make(ScheduledTrip, trips_year=trips_year)
        make_application(trips_year=trips_year, assigned_trip=trip)
        mommy.make(IncomingStudent, trips_year=trips_year, trip_assignment=trip)
        mommy.make(IncomingStudent, trips_year=trips_year, trip_assignment=trip)
        self.assertEqual(trip.size(), 3)



class QuickTestViews(WebTestCase):

    def test_index_views(self):
        
        trips_year = self.init_current_trips_year()
        director = self.mock_director()
        
        names = [
            'db:scheduledtrip_index',
            'db:triptemplate_index',
            'db:triptype_index',
            'db:campsite_index',
            'db:section_index',
            'db:leader_index',
        ]

        for name in names:
            res = self.app.get(reverse(name, kwargs={'trips_year': trips_year}), user=director)


class SectionManagerTestCase(TripsTestCase):
    
    def test_local(self):
        
        trips_year = self.init_current_trips_year()
        section1 = mommy.make(Section, trips_year=trips_year, is_local=True)
        section2 = mommy.make(Section, trips_year=trips_year, is_local=False)
        self.assertEqual([section1], list(Section.objects.local(trips_year)))

    def test_not_local(self):
        
        trips_year = self.init_current_trips_year()
        section1 = mommy.make(Section, trips_year=trips_year, is_local=True)
        section2 = mommy.make(Section, trips_year=trips_year, is_local=False)
        self.assertEqual([section2], list(Section.objects.not_local(trips_year)))

    def test_international(self):
        
        trips_year = self.init_current_trips_year()
        section1 = mommy.make(Section, trips_year=trips_year, is_international=True)
        section2 = mommy.make(Section, trips_year=trips_year, is_international=False)
        self.assertEqual([section1], list(Section.objects.international(trips_year)))

    def test_transfer(self):
        
        trips_year = self.init_current_trips_year()
        section1 = mommy.make(Section, trips_year=trips_year, is_transfer=True)
        section2 = mommy.make(Section, trips_year=trips_year, is_transfer=False)
        self.assertEqual([section1], list(Section.objects.transfer(trips_year)))

    def test_native(self):
        
        trips_year = self.init_current_trips_year()
        section1 = mommy.make(Section, trips_year=trips_year, is_native=True)
        section2 = mommy.make(Section, trips_year=trips_year, is_native=False)
        self.assertEqual([section1], list(Section.objects.native(trips_year)))

    def test_fysep(self):
        
        trips_year = self.init_current_trips_year()
        section1 = mommy.make(Section, trips_year=trips_year, is_fysep=True)
        section2 = mommy.make(Section, trips_year=trips_year, is_fysep=False)
        self.assertEqual([section1], list(Section.objects.fysep(trips_year)))

    def test_exchange(self):
        
        trips_year = self.init_current_trips_year()
        section1 = mommy.make(Section, trips_year=trips_year, is_exchange=True)
        section2 = mommy.make(Section, trips_year=trips_year, is_exchange=False)
        self.assertEqual([section1], list(Section.objects.exchange(trips_year)))


class SectionModelTestCase(TripsTestCase):
    
    def test_model_trip_dates(self):
        ty = self.init_current_trips_year()
        section = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
        self.assertEqual(section.trip_dates, 
                         [date(2015, 1, 2), date(2015, 1, 3), date(2015, 1, 4), date(2015, 1, 5), date(2015, 1, 6)])
        

class SectionDateManagerTestCase(TripsTestCase):
    
    def test_trips_dates_with_one_section(self):
        ty = self.init_current_trips_year()
        leaders_arrive = date(2015, 1, 1)
        section = mommy.make(Section, trips_year=ty, leaders_arrive=leaders_arrive)
        self.assertEqual(section.trip_dates, Section.dates.trip_dates(ty))

    def test_trips_dates_with_multiple_sections(self):
        ty = self.init_current_trips_year()
        section1 = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 1))
        section2 = mommy.make(Section, trips_year=ty, leaders_arrive=date(2015, 1, 4))
        self.assertEqual(Section.dates.trip_dates(ty),
                         sorted(list(set(section1.trip_dates + section2.trip_dates))))


class TripTemplateValidatorTest(unittest.TestCase):

    def test_validator(self):
        with self.assertRaises(ValidationError):
            validate_triptemplate_name(-1)
        with self.assertRaises(ValidationError):
            validate_triptemplate_name(1000)
        validate_triptemplate_name(0)
        validate_triptemplate_name(525)
        validate_triptemplate_name(999)

class AssignLeaderTestCase(WebTestCase):

    def test_trip_assignment_automatically_sets_LEADER_status(self):
        trips_year = self.init_current_trips_year()
        trip = mommy.make(ScheduledTrip, trips_year=trips_year)
        volunteer = make_application(trips_year=trips_year)
        volunteer.leader_supplement.available_sections.add(trip.section)
        volunteer.leader_supplement.available_triptypes.add(trip.template.triptype)
        url = reverse('db:assign_leader', kwargs={'trips_year': trips_year.pk, 'trip': trip.pk})
        res = self.app.get(url, user=self.mock_director())
        res = res.click(description="Assign to") 
        res.form.submit()  # assign to trip - first (and only) form on page
        volunteer = GeneralApplication.objects.get(pk=volunteer.pk)  # refresh
        self.assertEqual(volunteer.assigned_trip, trip)
        self.assertEqual(volunteer.status, GeneralApplication.LEADER)

    def test_assign_trip_computes_section_and_type_preferences(self):
        trips_year = self.init_current_trips_year()
        trip = mommy.make(ScheduledTrip, trips_year=trips_year)
        volunteer = make_application(trips_year=trips_year)
        volunteer.leader_supplement.available_sections.add(trip.section)
        volunteer.leader_supplement.preferred_triptypes.add(trip.template.triptype)
        url = reverse('db:assign_leader', kwargs={'trips_year': trips_year.pk, 'trip': trip.pk})
        res = self.app.get(url, user=self.mock_director())
        leader_list = list(res.context['leader_applications'])
        self.assertEqual(len(leader_list), 1)
        (leader, _, triptype_preference, section_preference) = leader_list[0]
        self.assertEqual(leader, volunteer)
        self.assertEqual(triptype_preference, 'prefer')
        self.assertEqual(section_preference, 'available')
        

class ScheduledTripManagerTestCase(TripsTestCase):
    
    def test_simple_matrix(self):
        trips_year = self.init_current_trips_year()
        template = mommy.make(TripTemplate, trips_year=trips_year)
        section = mommy.make(Section, trips_year=trips_year)
        trip = mommy.make(ScheduledTrip, section=section,
                          template=template, trips_year=trips_year)
        target = {template: {section: trip}}
        self.assertEqual(ScheduledTrip.objects.matrix(trips_year), target)

    def test_another_matrix(self):
        trips_year = self.init_current_trips_year()
        template1 = mommy.make(TripTemplate, trips_year=trips_year)
        section1 = mommy.make(Section, trips_year=trips_year)
        template2 = mommy.make(TripTemplate, trips_year=trips_year)
        section2 = mommy.make(Section, trips_year=trips_year)
        trip1 = mommy.make(ScheduledTrip, section=section1,
                           template=template1, trips_year=trips_year)
        trip2 = mommy.make(ScheduledTrip, section=section1,
                           template=template2, trips_year=trips_year)
        trip3 = mommy.make(ScheduledTrip, section=section2,
                           template=template2, trips_year=trips_year)
        target = {template1: {section1: trip1, section2: None},
                  template2: {section1: trip2, section2: trip3}}
        self.assertEqual(ScheduledTrip.objects.matrix(trips_year), target)


    def test_counts_are_equal(self):
        # tests that we are using Count(distinct=True)
        trips_year = self.init_current_trips_year()
        template = mommy.make(TripTemplate, trips_year=trips_year)
        section = mommy.make(Section, trips_year=trips_year)
        trip = mommy.make(ScheduledTrip, section=section,
                          template=template, trips_year=trips_year)
        mommy.make(IncomingStudent, trips_year=trips_year, trip_assignment=trip)
        mommy.make(GeneralApplication, trips_year=trips_year, assigned_trip=trip)
        mommy.make(GeneralApplication, trips_year=trips_year, assigned_trip=trip)
        matrix = ScheduledTrip.objects.matrix(trips_year)
        self.assertEqual(matrix[template][section].num_trippees, 1)
        self.assertEqual(matrix[template][section].num_trippees, matrix[template][section].trippees.count())


    def test_dropoffs(self):
        trips_year = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=trips_year)
        section = mommy.make(Section, trips_year=trips_year)
        dropoff = mommy.make(ScheduledTrip, trips_year=trips_year,
                             section=section, template__dropoff__route=route)
        overridden_dropoff = mommy.make(ScheduledTrip, trips_year=trips_year,
                                        section=section, dropoff_route=route)
        other_route = mommy.make(ScheduledTrip, trips_year=trips_year, 
                                 section=section)
        other_date = mommy.make(ScheduledTrip, trips_year=trips_year, 
                                template__dropoff__route=route,
                                section__leaders_arrive=section.leaders_arrive+timedelta(days=100))

        self.assertEqual(set([dropoff, overridden_dropoff]), 
                         set(ScheduledTrip.objects.dropoffs(route, section.at_campsite1, trips_year=trips_year)))

    def test_pickups(self):
        trips_year = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=trips_year)
        section = mommy.make(Section, trips_year=trips_year)
        pickup = mommy.make(ScheduledTrip, trips_year=trips_year,
                            section=section, template__pickup__route=route)
        overridden_pickup = mommy.make(ScheduledTrip, trips_year=trips_year,
                                       section=section, pickup_route=route)
        other_route = mommy.make(ScheduledTrip, trips_year=trips_year,
                                 section=section)
        other_date = mommy.make(ScheduledTrip, trips_year=trips_year,
                                template__pickup__route=route,
                                section__leaders_arrive=section.leaders_arrive+timedelta(days=100))

        self.assertEqual(set([pickup, overridden_pickup]),
                         set(ScheduledTrip.objects.pickups(route, section.arrive_at_lodge, trips_year=trips_year)))
        
    def test_returns(self):
        trips_year = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=trips_year)
        section = mommy.make(Section, trips_year=trips_year)
        returning = mommy.make(ScheduledTrip, trips_year=trips_year,
                            section=section, template__return_route=route)
        overridden_return = mommy.make(ScheduledTrip, trips_year=trips_year,
                                       section=section, return_route=route)
        other_route = mommy.make(ScheduledTrip, trips_year=trips_year,
                                 section=section)
        other_date = mommy.make(ScheduledTrip, trips_year=trips_year,
                                template__return_route=route,
                                section__leaders_arrive=section.leaders_arrive+timedelta(days=100))

        self.assertEqual(set([returning, overridden_return]),
                         set(ScheduledTrip.objects.returns(route, section.return_to_campus, trips_year=trips_year)))
    
