
from django.db import transaction
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from model_mommy import mommy

from trip.models import ScheduledTrip, Section, TripTemplate
from db.urlhelpers import reverse_create_url, reverse_update_url

from test.fixtures import WebTestCase

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
                                 user=self.director.net_id)
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
                                 user=self.director.net_id)
        # should have unique constraint error
        self.assertIn('unique constraint failed', str(response.content).lower())

        
        
        

