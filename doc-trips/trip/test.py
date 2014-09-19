
from django.db import transaction
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from model_mommy import mommy

from trip.models import ScheduledTrip, Section, TripTemplate
from db.urls import get_create_url, get_update_url

from test.fixtures import TestCase

class ScheduledTripTestCase(TestCase):
    
    csrf_checks = False

    def setUp(self):
        self.init_current_trips_year()

    def test_unique_validation_in_create_view(self):
        """ See the comment in DatabaseMixin.form_valid """
        self.mock_director()

        section = mommy.make(Section, trips_year=self.trips_year)
        section.save()
        template = mommy.make(TripTemplate, trips_year=self.trips_year)
        template.save()
        t1 = mommy.make(ScheduledTrip, trips_year=self.trips_year, section=section,
                        template=template)
        t1.save()

        #Posting will raise an IntegrityError if validation is not handled
        response = self.app.post(get_create_url(ScheduledTrip, self.trips_year), 
                                    {'template': template.pk, 
                                     'section': section.pk}, user=self.director.net_id)
        # should have unique constraint error
        self.assertIn('unique constraint failed', str(response.content).lower())
        # should not create the trip
        scheduled_trips = ScheduledTrip.objects.all()
        self.assertEquals(len(scheduled_trips), 1)
        self.assertEquals(scheduled_trips[0], t1)

    def test_unique_validation_in_update_view(self):
        self.mock_director()

        section = mommy.make(Section, trips_year=self.trips_year)
        section.save()
        template = mommy.make(TripTemplate, trips_year=self.trips_year)
        template.save()
        t1 = mommy.make(ScheduledTrip, trips_year=self.trips_year, section=section,
                        template=template)
        t1.save()

        t2 = mommy.make(ScheduledTrip, trips_year=self.trips_year)
        t2.save()

        #Posting will raise an IntegrityError if validation is not handled
        response = self.app.post(get_update_url(t2),
                                 {'template': template.pk, 
                                  'section': section.pk}, user=self.director.net_id)
        # should have unique constraint error
        self.assertIn('unique constraint failed', str(response.content).lower())

        
        
        

