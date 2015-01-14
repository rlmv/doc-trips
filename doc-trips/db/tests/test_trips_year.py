
from django.test.utils import override_settings
from django.conf.urls import url, patterns
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from vanilla import DetailView, TemplateView, View
from model_mommy import mommy

from test.fixtures import WebTestCase
from db.views import TripsYearMixin
from trip.models import Campsite, TripTemplate

from db.urlhelpers import reverse_create_url, reverse_update_url, reverse_index_url


class TripsYearMixinTestCase(WebTestCase):

    """ Integration tests for TripsYearMixin. 

    Specifically checks that objects with separate trips_years do
    not get mixed up. 
    """

    csrf_checks = False

    def setUp(self):
        self.init_current_trips_year()
        self.init_old_trips_year()


    def test_dispatch_for_trips_year(self):
        self.mock_director()
        year = self.init_current_trips_year()
        response = self.app.get('/db/'+str(year.year)+'/', user=self.director.net_id)
        self.assertEquals(response.status_code, 200)


    def test_dispatch_for_nonexistant_year(self):
        self.mock_director()
        response = self.app.get('/db/2314124/', status=404, user=self.director.net_id)
        self.assertEquals(response.status_code, 404)


    def test_trips_year_is_added_to_models_by_create_form_submission(self):
        """ Use Campsite as model, instead of hacking together an example"""

        self.mock_director()
       
        data = model_to_dict(mommy.prepare(Campsite))
        response = self.app.post(reverse_create_url(Campsite, self.current_trips_year), 
                                 data, 
                                 user=self.director.net_id)

        # should not display form error in page
        self.assertNotIn('NOT NULL constraint failed', str(response.content))

        # should have object in the database
        c = Campsite.objects.get(name=data['name'])
        self.assertEquals(c.trips_year, self.current_trips_year)

        
    def test_trips_year_queryset_filtering(self):
        """ 
        Check that *only* objects for the requested trips_year are in 
        a database list view. 
        """
        
        self.mock_director()

        ex1 = mommy.make(Campsite, trips_year=self.trips_year)
        ex2 = mommy.make(Campsite, trips_year=self.old_trips_year)

        response = self.app.get(reverse_index_url(ex1), user=self.director.net_id)
        
        from trip.views import CampsiteListView
        objects = response.context[CampsiteListView.context_object_name]
        self.assertEqual(len(objects), 1, 'should only get one object')
        self.assertEqual(objects[0], ex1, 'should get object with matching trips_year')

    def test_UpdateView_routing_rejects_mismatched_TripsYear(self):

        self.mock_director()
        c1 = mommy.make(Campsite, trips_year=self.trips_year)
        c2 = mommy.make(Campsite, trips_year=self.old_trips_year)
        
        # good request - trips year in url matches trips year of c1
        response = self.app.get(reverse_update_url(c1), user=self.director.net_id)
        object = response.context['object']
        self.assertEquals(object, c1)
        
        # bad request
        response = self.app.get(reverse('db:campsite_update', 
                                        kwargs={'trips_year': c1.trips_year.year, 
                                                'pk': c2.pk}),
                                expect_errors=True)
        self.assertEquals(response.status_code, 404, 'should not find c2 because trips_year does not match c2.trips_year')

    def test_related_objects_in_form_have_same_trips_year_as_main_object(self):
        
        self.mock_director()

        c1 = mommy.make(Campsite, trips_year=self.trips_year)
        c2 = mommy.make(Campsite, trips_year=self.old_trips_year)
        triptemplate = mommy.make(TripTemplate, trips_year=self.trips_year)
        
        response = self.app.get(reverse_update_url(triptemplate), 
                                user=self.director.net_id)
        choices = response.context['form'].fields['campsite_1'].queryset

        # should only show object from current_trips_year
        self.assertEquals(len(choices), 1)
        self.assertTrue(c1 in choices)
        self.assertTrue(c2 not in choices)




