from django.urls import reverse
from django.forms.models import model_to_dict
from model_mommy import mommy

from fyt.db.views import TripsYearMixin
from fyt.test import FytTestCase
from fyt.trips.models import Campsite, Section, TripTemplate, TripType


class TripsYearMixinTestCase(FytTestCase):
    """ Integration tests for TripsYearMixin. """

    csrf_checks = False

    def setUp(self):
        self.init_trips_year()
        self.init_old_trips_year()

    def test_dispatch_for_trips_year(self):
        year = self.init_trips_year()
        response = self.app.get('/db/'+str(year.year)+'/',
                                user=self.make_director())
        self.assertEquals(response.status_code, 200)

    def test_dispatch_for_nonexistant_year(self):
        response = self.app.get('/db/2314124/', status=404,
                                user=self.make_director())
        self.assertEquals(response.status_code, 404)

    def test_trips_year_is_added_to_models_by_create_form_submission(self):
        """Use Section as model, instead of hacking together an example"""
        data = model_to_dict(mommy.prepare(Section))
        url = Section.create_url(self.trips_year)
        response = self.app.post(url, params=data, user=self.make_director())

        # should not display form error in page
        self.assertNotIn('NOT NULL constraint failed', str(response.content))

        # should have object in the database
        s = Section.objects.get(name=data['name'])
        self.assertEquals(s.trips_year, self.trips_year)

    def test_trips_year_queryset_filtering(self):
        """
        Check that *only* objects for the requested trips_year are in
        a database list view.
        """
        ex1 = mommy.make(TripType, trips_year=self.trips_year)
        ex2 = mommy.make(TripType, trips_year=self.old_trips_year)

        response = self.app.get(ex1.index_url(), user=self.make_director())

        from fyt.trips.views import TripTypeList
        objects = response.context[TripTypeList.context_object_name]
        self.assertEqual(len(objects), 1, 'should only get one object')
        self.assertEqual(objects[0], ex1, 'should get object for `trips_year`')

    def test_UpdateView_routing_rejects_mismatched_TripsYear(self):
        c1 = mommy.make(Campsite, trips_year=self.trips_year)
        c2 = mommy.make(Campsite, trips_year=self.old_trips_year)

        self.make_director()

        # good request - trips year in url matches trips year of c1
        response = self.app.get(c1.update_url(), user=self.director)
        object = response.context['object']
        self.assertEquals(object, c1)

        # bad request
        url = reverse('db:campsite:update', kwargs={
            'trips_year': c1.trips_year.year, 'pk': c2.pk})

        response = self.app.get(url, expect_errors=True, user=self.director)
        self.assertEquals(response.status_code, 404,
            'should not find c2 because `trips_year != c2.trips_year`')

    def test_related_objects_in_form_have_same_trips_year_as_main_object(self):
        c1 = mommy.make(Campsite, trips_year=self.trips_year)
        c2 = mommy.make(Campsite, trips_year=self.old_trips_year)
        triptemplate = mommy.make(TripTemplate, trips_year=self.trips_year)

        response = self.app.get(triptemplate.update_url(),
                                user=self.make_director())
        choices = response.context['form'].fields['campsite1'].queryset

        # should only show object from current_trips_year
        self.assertEquals(len(choices), 1)
        self.assertTrue(c1 in choices)
        self.assertTrue(c2 not in choices)

    def test_get_trips_year(self):
        view = TripsYearMixin()
        view.kwargs = {'trips_year': self.trips_year}
        self.assertEqual(view.get_trips_year(), self.trips_year)
