from model_mommy import mommy

from fyt.applications.models import (
    Score,
    Grader
)
from fyt.test import FytTestCase


class GraderViewsTestCase(FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.init_old_trips_year()
        self.make_user()
        self.grader = Grader.objects.from_user(self.make_grader())

    def test_for_year_only_returns_graders(self):
        mommy.make(Score, trips_year=self.trips_year, grader=self.grader)
        self.assertQsEqual(Grader.objects.for_year(self.trips_year),
                           [self.grader])

    def test_for_year_returns_distinct_queryset(self):
        mommy.make(Score, 2, trips_year=self.trips_year, grader=self.grader)
        self.assertQsEqual(Grader.objects.for_year(self.trips_year),
                           [self.grader])

    def test_for_year_filters_trips_year(self):
        new_score = mommy.make(Score, trips_year=self.trips_year)
        old_score = mommy.make(Score, trips_year=self.old_trips_year)
        self.assertQsEqual(Grader.objects.for_year(self.trips_year),
                           [new_score.grader])

    def test_for_year_averages_only_include_scores_from_this_year(self):
        mommy.make(
            Score,
            trips_year=self.trips_year,
            grader=self.grader,
            leader_score=1,
            croo_score=2,
        )
        mommy.make(
            Score,
            trips_year=self.old_trips_year,
            grader=self.grader,
            leader_score=3,
            croo_score=4
        )
        graders = Grader.objects.for_year(self.trips_year)
        self.assertEqual(len(graders), 1)
        self.assertEqual(graders[0].score_count, 1)
        self.assertEqual(graders[0].avg_leader_score, 1)
        self.assertEqual(graders[0].avg_croo_score, 2)

    def test_for_year_score_histogram(self):
        mommy.make(
            Score,
            trips_year=self.trips_year,
            grader=self.grader,
            leader_score=1,
            croo_score=2,
        )
        mommy.make(
            Score,
            trips_year=self.trips_year,
            grader=self.grader,
            leader_score=4,
            croo_score=4
        )
        graders = Grader.objects.for_year(self.trips_year)

        self.assertEqual(graders[0].leader_score_histogram, {
            1: 1,
            1.5: 0,
            2: 0,
            2.5: 0,
            3: 0,
            3.5: 0,
            4: 1,
            4.5: 0,
            5: 0,
        })
        self.assertEqual(graders[0].croo_score_histogram, {
            1: 0,
            1.5: 0,
            2: 1,
            2.5: 0,
            3: 0,
            3.5: 0,
            4: 1,
            4.5: 0,
            5: 0,
        })
