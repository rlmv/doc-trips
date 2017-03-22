from django.core.exceptions import ValidationError
from model_mommy.recipe import Recipe, foreign_key

from fyt.db.mommy_recipes import trips_year as trips_year_recipe
from fyt.raids.models import Raid
from fyt.test.testcases import FytTestCase


raid_recipe = Recipe(Raid, trips_year=foreign_key(trips_year_recipe))


class RaidModelsTestCase(FytTestCase):

    def test_raid_requires_trip_or_campsite(self):
        with self.assertRaises(ValidationError):
            raid_recipe.prepare(campsite=None, trip=None).full_clean()


class RaidViewsTestCase(FytTestCase):

    def test_only_directors_can_delete_raids(self):
        trips_year = trips_year_recipe.make()
        raid = raid_recipe.make(trips_year=trips_year)
        url = raid.delete_url()
        self.app.get(url, user=self.mock_user(), status=403)  # No good
        resp = self.app.get(url, user=self.mock_director())  # OK
        resp.form.submit()
        with self.assertRaises(Raid.DoesNotExist):
            Raid.objects.get()

    def test_only_directors_can_see_delete_link(self):
        trips_year = trips_year_recipe.make()
        raid = raid_recipe.make(trips_year=trips_year)

        resp = self.app.get(raid.detail_url(), user=self.mock_user())
        self.assertNotContains(resp, 'delete')

        resp = self.app.get(raid.detail_url(), user=self.mock_director())
        self.assertContains(resp, 'delete')
