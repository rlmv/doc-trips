from django.core.exceptions import ValidationError
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from doc.test.testcases import TripsTestCase, WebTestCase
from doc.db.models import TripsYear
from doc.db.mommy_recipes import trips_year
from doc.raids.models import Raid, Comment


class RaidModelsTestCase(TripsTestCase):

    def setUp(self):
        self.raid = Recipe(
            Raid,
            trips_year=foreign_key(trips_year)
        )

    def test_raid_requires_trip_or_campsite(self):
        with self.assertRaises(ValidationError):
            self.raid.prepare(campsite=None, trip=None).full_clean()
