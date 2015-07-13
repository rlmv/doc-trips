import unittest

from django.db import models
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.conf.urls import patterns, url, include
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError, FieldError
from model_mommy import mommy

from doc.test.fixtures import WebTestCase, TripsYearTestCase
from doc.db.models import DatabaseModel, TripsYear
from doc.db.urlhelpers import reverse_update_url, reverse_create_url, reverse_index_url
from doc.trips.models import Campsite, TripTemplate
from doc.db.forms import tripsyear_modelform_factory


class DatabaseModelTestCase(TripsYearTestCase):

    def setUp(self):
        self.init_current_trips_year()

    def test_trips_year_field_is_required(self):
        self.assertRaises(ValueError, mommy.make, Campsite, trips_year=None)

class DatabaseMixinTestCase(WebTestCase):
    
    """ DatabaseMixin integration tests """

    csrf_checks = False

    def setUp(self):
        self.init_current_trips_year()
        self.init_old_trips_year()

    def test_need_database_permissions_to_access_database_pages(self):

        campsite = mommy.make(Campsite, trips_year=self.trips_year)
        url = reverse_update_url(campsite)
        
        self.mock_user()
        self.app.get(url, user=self.user.netid, expect_errors=True)

        self.mock_director()
        response = self.app.get(url, user=self.director.netid)
        self.assertEquals(response.status_code, 200)

    
class FormFieldCallbackTestCase(TripsYearTestCase):

    def setUp(self):
        self.init_current_trips_year()
    
    def test_formfield_callback_for_non_DatabaseModel_fields_does_not_raise_error(self):
        tripsyear_modelform_factory(Campsite, self.current_trips_year)



