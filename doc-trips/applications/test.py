
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from model_mommy import mommy

from test.fixtures import TripsYearTestCase as TripsTestCase, WebTestCase


class ApplicationAccessTestCase(WebTestCase):

    def setUp(self):
        self.init_current_trips_year()

    def test_anonymous_user_does_not_crash_application(self):
        
        self.app.get(reverse('applications:apply'))


    
