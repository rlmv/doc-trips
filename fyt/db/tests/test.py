from model_mommy import mommy
from django.db import IntegrityError

from fyt.test.testcases import WebTestCase, TripsYearTestCase
from fyt.trips.models import Campsite, TripTemplate
from fyt.db.forms import tripsyear_modelform_factory


class DatabaseModelTestCase(TripsYearTestCase):

    def test_trips_year_field_is_required(self):
        self.assertRaises(IntegrityError, mommy.make, Campsite, trips_year=None)

    def test_model_name_lower(self):
        self.assertEqual(TripTemplate.model_name_lower(), 'triptemplate')

        # Should also work for deferred models, which are dynamically created
        mommy.make(TripTemplate)
        triptemplate = TripTemplate.objects.defer('name').get()
        self.assertEqual(triptemplate.model_name_lower(), 'triptemplate')


class DatabaseMixinTestCase(WebTestCase):
    """ DatabaseMixin integration tests """
    csrf_checks = False

    def test_need_database_permissions_to_access_database_pages(self):
        trips_year = self.init_current_trips_year()
        campsite = mommy.make(Campsite, trips_year=trips_year)

        url = campsite.update_url()
        self.app.get(url, user=self.mock_user(), status=403)
        self.app.get(url, user=self.mock_director(), status=200)


class RedirectToCurrentDatabaseTestCase(WebTestCase):

    def test_db_redirect_access_without_permissions(self):
        trips_year = self.init_trips_year()
        self.app.get('/db/', user=self.mock_user(), status=403)


class FormFieldCallbackTestCase(TripsYearTestCase):

    def test_formfield_callback_for_non_DatabaseModel_fields_does_not_raise_error(self):
        trips_year = self.init_trips_year()
        tripsyear_modelform_factory(Campsite, trips_year, fields='__all__')
