
from django.test import TestCase
from django.db import models
from django.test.utils import override_settings
from django.conf.urls import patterns, url
from model_mommy import mommy

from db.models import DatabaseModel, TripsYear
from test.fixtures import init_trips_year


class ExampleDatabaseModel(DatabaseModel):
    """ Mock class inheriting DatabaseModel """
    some_field = models.CharField(max_length=255)


""" Test urls for test_get_absolute_url """
urlpatterns = patterns('', 
    url(r'^(?P<trips_year>[0-9]+)/(?P<pk>[0-9]+)$', lambda r: None, name='test_url')
)


class DatabaseModelTestCase(TestCase):

    def setUp(self):
        self.trips_year = init_trips_year()

    def test_trips_year_automatic_addition_to_database_models(self):
        
        e = ExampleDatabaseModel(some_field='hi')
        e.save()
        self.assertEqual(e.trips_year, self.trips_year, 
                         'saving should add current trips_year to new model instances')

        other_trips_year = TripsYear(year=1937)
        e2 = ExampleDatabaseModel(some_field='bye', trips_year=other_trips_year)
        e2.save()
        self.assertNotEqual(e2.trips_year, self.trips_year, 
                            'saving should not overide explicitly specified trip_year')

    @override_settings(ROOT_URLCONF='db.test.test')
    def test_get_absolute_url(self):
        
        e = ExampleDatabaseModel(some_field='ocho')
        e.save()
        e.absolute_url_pattern = 'test_url'
        e.get_absolute_url()


class CalendarTestCase(TestCase):

    def setUp(self):
        init_trips_year()
