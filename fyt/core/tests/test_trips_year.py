from django.forms.models import model_to_dict
from django.urls import reverse
from model_mommy import mommy

from fyt.core.forms import TripsYearModelForm
from fyt.core.views import DatabaseUpdateView, TripsYearMixin
from fyt.incoming.models import Registration
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
        response = self.app.get('/db/{}/'.format(year.year),
                                user=self.make_director())
        self.assertEqual(response.status_code, 200)

    def test_dispatch_for_nonexistant_year(self):
        response = self.app.get('/db/2314124/', status=404,
                                user=self.make_director())
        self.assertEqual(response.status_code, 404)

    def test_trips_year_is_added_to_models_by_create_form_submission(self):
        """Use Section as model, instead of hacking together an example"""
        data = model_to_dict(mommy.prepare(Section))
        url = Section.create_url(self.trips_year)
        response = self.app.post(url, params=data, user=self.make_director())

        # should not display form error in page
        self.assertNotIn('NOT NULL constraint failed', str(response.content))

        # should have object in the database
        s = Section.objects.get(name=data['name'])
        self.assertEqual(s.trips_year, self.trips_year)

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
        self.assertEqual(object, c1)

        # bad request
        url = reverse('core:campsite:update', kwargs={
            'trips_year': c1.trips_year.year, 'pk': c2.pk})

        response = self.app.get(url, expect_errors=True, user=self.director)
        self.assertEqual(response.status_code, 404,
            'should not find c2 because `trips_year != c2.trips_year`')

    def test_related_objects_in_form_have_same_trips_year_as_main_object(self):
        c1 = mommy.make(Campsite, trips_year=self.trips_year)
        c2 = mommy.make(Campsite, trips_year=self.old_trips_year)
        triptemplate = mommy.make(TripTemplate,
                                  trips_year=self.trips_year,
                                  description__trips_year=self.trips_year)

        response = self.app.get(triptemplate.update_url(),
                                user=self.make_director())
        choices = response.context['form'].fields['campsite1'].queryset

        # should only show object from current_trips_year
        self.assertEqual(len(choices), 1)
        self.assertTrue(c1 in choices)
        self.assertTrue(c2 not in choices)

    def test_get_trips_year(self):
        view = TripsYearMixin()
        view.kwargs = {'trips_year': self.trips_year.year}
        self.assertEqual(view.trips_year, self.trips_year)


class TripsYearModelFormTestCase(FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.init_old_trips_year()

    def test_form_filters_related_trips_year(self):
        campsite = mommy.make(Campsite, trips_year=self.trips_year)
        campsite_old = mommy.make(Campsite, trips_year=self.old_trips_year)
        triptemplate = mommy.make(TripTemplate, trips_year=self.trips_year)

        class TripTemplateForm(TripsYearModelForm):
            class Meta:
                model = TripTemplate
                fields = ['campsite1', 'campsite2']

        form = TripTemplateForm(trips_year=self.trips_year)
        self.assertQsEqual(form.fields['campsite1'].queryset, [campsite])
        self.assertQsEqual(form.fields['campsite2'].queryset, [campsite])

    def test_form_filters_related_trips_year_for_m2m(self):
        section = mommy.make(Section, trips_year=self.trips_year)
        section_old = mommy.make(Section, trips_year=self.old_trips_year)

        class RegistrationSectionPreferenceForm(TripsYearModelForm):
            class Meta:
                model = Registration
                fields = ['section_choice']

        form = RegistrationSectionPreferenceForm(trips_year=self.trips_year)
        self.assertQsEqual(form.fields['section_choice'].queryset, [section])

    def test_pull_trips_year_from_instance_if_provided(self):
        triptemplate = mommy.make(TripTemplate, trips_year=self.trips_year)

        class TripTemplateForm(TripsYearModelForm):
            class Meta:
                model = TripTemplate
                fields = '__all__'

        form = TripTemplateForm(instance=triptemplate)
        self.assertEqual(form.trips_year, self.trips_year)

    def test_explicit_and_instance_trips_years_match(self):
        triptemplate = mommy.make(TripTemplate, trips_year=self.trips_year)

        class TripTemplateForm(TripsYearModelForm):
            class Meta:
                model = TripTemplate
                fields = '__all__'

        with self.assertRaises(ValueError):
            TripTemplateForm(trips_year=self.old_trips_year,
                             instance=triptemplate)


class DetailViewTestCase(FytTestCase):

    def test_urls_in_context(self):
        trips_year = self.init_trips_year()
        # test Section detail, for example
        section = mommy.make(Section, trips_year=trips_year)
        resp = self.app.get(section.detail_url(), user=self.make_director())
        self.assertEqual(resp.context['update_url'], section.update_url())
        self.assertEqual(resp.context['delete_url'], section.delete_url())


class UpdateViewTestCase(FytTestCase):

    def test_form_has_crispy_helper(self):
        trips_year = self.init_trips_year()
        view = DatabaseUpdateView()
        view.model = TripTemplate
        view.object = mommy.make(TripTemplate, trips_year=trips_year)
        view.kwargs = {'trips_year': trips_year.pk}
        form = view.get_form()
        self.assertIsNotNone(form.helper)
