
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
        """ See the comment in DatabaseMixin.form_valid 

        Posting will raise an IntegrityError if validation is not handled"""

        t1 = mommy.make(ScheduledTrip, trips_year=self.trips_year)
        t1.save()

        response = self.client.post(ScheduledTrip.get_create_url(self.trips_year), 
                                    {'template': t1.template.pk, 'section': t1.section.pk})
        
        
        
        
        

