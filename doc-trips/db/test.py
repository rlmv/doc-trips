
from django.test import TestCase
from django.db import models
from django.test.utils import override_settings
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from model_mommy import mommy

from db.models import DatabaseModel, TripsYear
from test.fixtures import init_trips_year


class ExampleDatabaseModel(DatabaseModel):
    """ Mock class inheriting DatabaseModel """
    some_field = models.CharField(max_length=255)


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


from db.views import DatabaseMixin
from vanilla import ListView, UpdateView
class ExampleListView(DatabaseMixin, ListView):
    model = ExampleDatabaseModel
    template_name = 'db/list.html'
    context_object_name = 'objects'

class ExampleUpdateView(DatabaseMixin, UpdateView):
    model = ExampleDatabaseModel
    template_name = 'db/update.html'
    context_object_name = 'object'

urlpatterns = patterns('',
    url(r'^(?P<trips_year>[0-9]+)/$', ExampleListView.as_view(), name='test_listview'), 
    url(r'^(?P<trips_year>[0-9]+)/(?P<pk>[0-9]+)/$', ExampleUpdateView.as_view(), name='test_updateview'),
)

@override_settings(ROOT_URLCONF='db.test')
class DatabaseMixinTestCase(TestCase):

    """ Tests for DatabseMixin. We use mix the class into custom views,
    instead of using DatabaseListView etc. because we can't easily test 
    the companion LoginRequiredMixin. 
    """

    def setUp(self):
        self.current_trips_year = init_trips_year()
        self.old_trips_year = mommy.make(TripsYear, is_current=False)
        self.old_trips_year.save()
    
    def test_trips_year_queryset_filtering(self):
        
        ex1 = mommy.make(ExampleDatabaseModel, trips_year=self.current_trips_year)
        ex1.save()
        ex2 = mommy.make(ExampleDatabaseModel, trips_year=self.old_trips_year)
        ex2.save()

        response = self.client.get(reverse('test_listview', kwargs={'trips_year': self.current_trips_year.pk}))
        
        objects = response.context[ExampleListView.context_object_name]
        self.assertEqual(len(objects), 1, 'should only get one object')
        self.assertEqual(objects[0], ex1, 'should get object with matching trips_year')


    def test_trips_year_update_view_queryset_filtering(self):
        ex1 = mommy.make(ExampleDatabaseModel, trips_year=self.current_trips_year)
        ex1.save()
        ex2 = mommy.make(ExampleDatabaseModel, trips_year=self.old_trips_year)
        ex2.save()

        kwargs = {'trips_year' : self.current_trips_year.year, 
                  'pk': ex1.pk}
        response = self.client.get(reverse('test_updateview', kwargs=kwargs))
        object = response.context[ExampleUpdateView.context_object_name]
        self.assertEquals(object, ex1)

        kwargs = {'trips_year' : self.current_trips_year.year, 
                  'pk': ex2.pk}
        response = self.client.get(reverse('test_updateview', kwargs=kwargs))
        self.assertEquals(response.status_code, 404, 'should not find ex2 because trips_year does not match ex2.trips_year')
        

class CalendarTestCase(TestCase):

    def setUp(self):
        init_trips_year()
