
from django.db import transaction
from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from model_mommy import mommy

from trip.models import ScheduledTrip
from test.fixtures import initialize_trips_year, mock_login


class ScheduledTripTestCase(TestCase):

    def setUp(self):
        initialize_trips_year(self)
        mock_login(self)

    def test_unique_validation_in_create_view(self):
        """ See the comment in DatabaseMixin.form_valid """


        t1 = mommy.make(ScheduledTrip, trips_year=self.trips_year)
        t1.save()

        #Posting will raise an IntegrityError if validation is not handled
        response = self.client.post(ScheduledTrip.get_create_url(self.trips_year), 
                                    {'template': t1.template.pk, 'section': t1.section.pk})
        
        self.assertGreater(len(response.context['form'].non_field_errors().as_data()), 0, 
                           'should have an error message')
        
        # should not create the trip
        scheduled_trips = ScheduledTrip.objects.all()
        self.assertEquals(len(scheduled_trips), 1)
        self.assertEquals(scheduled_trips[0], t1)
        
        
        
        

