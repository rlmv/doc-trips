import io

from django.core.management import call_command
from django.db import IntegrityError
from model_mommy import mommy

from fyt.core.forms import tripsyear_modelform_factory
from fyt.core.models import TripsYear
from fyt.test import FytTestCase
from fyt.trips.models import Campsite, TripTemplate


class InitialDataTestCase(FytTestCase):
    '''Test that initial data is loaded into a fresh database.'''

    def test_bootstrap(self):
        out = io.StringIO()  # Redirect command output
        call_command('bootstrap', stdout=out)
        self.assertEqual(TripsYear.objects.current().year, 2017)


class DatabaseModelTestCase(FytTestCase):

    def test_trips_year_field_is_required(self):
        self.assertRaises(IntegrityError, mommy.make, Campsite, trips_year=None)

    def test_model_name_lower(self):
        self.assertEqual(TripTemplate.model_name_lower(), 'triptemplate')

        # Should also work for deferred models, which are dynamically created
        mommy.make(TripTemplate)
        triptemplate = TripTemplate.objects.defer('name').get()
        self.assertEqual(triptemplate.model_name_lower(), 'triptemplate')


class DatabaseMixinTestCase(FytTestCase):
    """ DatabaseMixin integration tests """
    csrf_checks = False

    def test_need_database_permissions_to_access_database_pages(self):
        trips_year = self.init_trips_year()
        campsite = mommy.make(Campsite, trips_year=trips_year)

        url = campsite.update_url()
        self.app.get(url, user=self.make_user(), status=403)
        self.app.get(url, user=self.make_director(), status=200)


class RedirectToCurrentDatabaseTestCase(FytTestCase):

    def test_db_redirect_access_without_permissions(self):
        trips_year = self.init_trips_year()
        self.app.get('/db/', user=self.make_user(), status=403)


class FormFieldCallbackTestCase(FytTestCase):

    def test_formfield_callback_for_non_DatabaseModel_fields_does_not_raise_error(self):
        trips_year = self.init_trips_year()
        tripsyear_modelform_factory(Campsite, trips_year, fields='__all__')
