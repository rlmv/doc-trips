
from django.db import models
from django.test.utils import override_settings
from django.conf.urls import patterns, url, include
from django.core.urlresolvers import reverse
from model_mommy import mommy

from db.models import DatabaseModel, TripsYear
from db.urls import get_update_url
from test import TestCase


class ExampleDatabaseModel(DatabaseModel):
    """ Mock class inheriting DatabaseModel """
    some_field = models.CharField(max_length=255)
    related_field = models.ForeignKey('self', null=True)

class DatabaseModelTestCase(TestCase):

    def setUp(self):
        self.init_current_trips_year()

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


from db.views import DatabaseUpdateView, DatabaseListView, DatabaseDeleteView
class ExampleListView(DatabaseListView):
    model = ExampleDatabaseModel
    template_name = 'db/list.html'
    context_object_name = 'objects'

class ExampleUpdateView(DatabaseUpdateView):
    model = ExampleDatabaseModel
    context_object_name = 'wingding'

class ExampleDeleteView(DatabaseDeleteView):
    model = ExampleDatabaseModel
    context_object_name = 'hjeeeeeeeelllp'


example_urlpatterns = patterns('', 
    ExampleListView.urlpattern(),                           
    ExampleUpdateView.urlpattern(),
    ExampleDeleteView.urlpattern(),                           
)
urlpatterns = patterns('', 
    url(r'^(?P<trips_year>[0-9]+)/', include(example_urlpatterns, namespace='db'))
)

from user.permissions import *
from db.urls import get_update_url, get_index_url

@override_settings(ROOT_URLCONF='db.test')
class DatabaseMixinTestCase(TestCase):

    """ Tests for DatabseMixin. """

    def setUp(self):
        self.init_current_trips_year()
        self.init_old_trips_year()


    def test_need_database_permissions_to_access_database_pages(self):

        ex1 = mommy.make(ExampleDatabaseModel, trips_year=self.trips_year)
        ex1.save()
        db_url = get_update_url(ex1)
        
        response = self.client.get(db_url)
        # TODO: 
        

    def test_trips_year_queryset_filtering(self):

        self.mock_director_login()

        ex1 = mommy.make(ExampleDatabaseModel, trips_year=self.trips_year)
        ex1.save()
        ex2 = mommy.make(ExampleDatabaseModel, trips_year=self.old_trips_year)
        ex2.save()

        response = self.client.get(get_index_url(ex1))
        
        objects = response.context[ExampleListView.context_object_name]
        self.assertEqual(len(objects), 1, 'should only get one object')
        self.assertEqual(objects[0], ex1, 'should get object with matching trips_year')

    def test_trips_year_update_view_filters_trips_year(self):

        self.mock_director_login()

        ex1 = mommy.make(ExampleDatabaseModel, trips_year=self.trips_year)
        ex1.save()
        ex2 = mommy.make(ExampleDatabaseModel, trips_year=self.old_trips_year)
        ex2.save()

        response = self.client.get(get_update_url(ex1))
        object = response.context[ExampleUpdateView.context_object_name]
        self.assertEquals(object, ex1)
        
        response = self.client.get(reverse('db:exampledatabasemodel_update', 
                                           kwargs={'trips_year': ex1.trips_year.year, 
                                                   'pk': ex2.pk}))
        self.assertEquals(response.status_code, 404, 'should not find ex2 because trips_year does not match ex2.trips_year')


    def test_related_objects_in_form_has_same_trips_year_as_main_object(self):
        
        self.mock_director_login()

        ex1 = mommy.make(ExampleDatabaseModel, trips_year=self.trips_year)
        ex1.save()
        ex2 = mommy.make(ExampleDatabaseModel, trips_year=self.old_trips_year)
        ex2.save()
        ex3 = mommy.make(ExampleDatabaseModel, trips_year=self.trips_year)
        ex3.save()
        
        response = self.client.get(get_update_url(ex1))
        choices = response.context['form'].fields['related_field'].queryset

        # should only show objects from current_trips_year
        self.assertTrue(len(choices) == 2)
        self.assertTrue(ex1 in choices)
        self.assertTrue(ex2 not in choices)
        self.assertTrue(ex3 in choices)
        

class CalendarTestCase(TestCase):

    def setUp(self):
        init_trips_year()
