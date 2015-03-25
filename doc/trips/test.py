from datetime import date
from django.db import transaction
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from model_mommy import mommy

from doc.trips.models import ScheduledTrip, Section, TripTemplate
from doc.db.urlhelpers import reverse_create_url, reverse_update_url

from doc.test.fixtures import WebTestCase, TripsYearTestCase as TripsTestCase

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

    def test_unique_validation_in_update_view(self):
        self.mock_director()

        trip = mommy.make(ScheduledTrip, trips_year=self.trips_year, 
                        template__trips_year=self.trips_year,
                        section__trips_year=self.trips_year)
        trip.save()

        trip2 = mommy.make(ScheduledTrip, trips_year=self.trips_year)
        trip2.save()

        #Posting will raise an IntegrityError if validation is not handled
        response = self.app.post(reverse_update_url(trip2),
                                 {'template': trip.template.pk, 
                                  'section': trip.section.pk}, 
                                 user=self.director.netid)
        # should have unique constraint error
        self.assertIn('unique constraint failed', str(response.content).lower())


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
