import unittest

from django.db import models
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.conf.urls import patterns, url, include
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError, FieldError
from model_mommy import mommy

from db.models import DatabaseModel, TripsYear
from db.urls import get_update_url, get_create_url
from test import TestCase


class ExampleDatabaseModel(DatabaseModel):
    """ Mock class inheriting DatabaseModel """
    some_field = models.CharField(max_length=255)
    related_field = models.ForeignKey('self', null=True)
    non_database_related_field = models.ForeignKey(get_user_model(), null=True, blank=True)

class DatabaseModelTestCase(TestCase):

    def setUp(self):
        self.init_current_trips_year()


    def test_trips_year_field_is_required(self):
        self.assertRaises(ValueError, mommy.make, ExampleDatabaseModel, trips_year=None)


from db.views import DatabaseUpdateView, DatabaseListView, DatabaseDeleteView, DatabaseCreateView
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

class ExampleCreateView(DatabaseCreateView):
    model = ExampleDatabaseModel
    success_url = '/'

example_urlpatterns = patterns('', 
    ExampleListView.urlpattern(),                           
    ExampleUpdateView.urlpattern(),
    ExampleDeleteView.urlpattern(),                           
    ExampleCreateView.urlpattern(),                               
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
        

    def test_trips_year_is_added_to_models_by_create_form_submission(self):
 
        self.mock_director_login()
        ex = mommy.make(ExampleDatabaseModel, trips_year=self.current_trips_year)

        phrase = 'very specific phrase'
        response = self.client.post(get_create_url(ExampleDatabaseModel, 
                                                   self.current_trips_year), 
                                    {'some_field': phrase, 'related_field': ex.pk})


        # should not display form error in page
        self.assertNotIn('NOT NULL constraint failed', str(response.content))

        # should have object in the database
        ex = ExampleDatabaseModel.objects.get(some_field=phrase)
        self.assertEquals(ex.trips_year, self.current_trips_year)

        
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

    def test_related_objects_in_form_have_same_trips_year_as_main_object(self):
        
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
        self.assertEquals(len(choices), 2)
        self.assertTrue(ex1 in choices)
        self.assertTrue(ex2 not in choices)
        self.assertTrue(ex3 in choices)
        
    
class FormFieldCallbackTestCase(TestCase):

    def setUp(self):
        self.init_current_trips_year()
    
    def test_formfield_callback_for_non_DatabaseModel_fields_does_not_raise_error(self):
        from db.views import make_formfield_callback
        from django.forms.models import modelform_factory

        callback = make_formfield_callback(self.current_trips_year)
        modelform_factory(ExampleDatabaseModel, formfield_callback=callback)

class CalendarTestCase(TestCase):

    def setUp(self):
        init_trips_year()
