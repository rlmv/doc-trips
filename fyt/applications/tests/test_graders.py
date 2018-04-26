from model_mommy import mommy

from .tests import ApplicationTestMixin

from fyt.applications.models import Grader, Score
from fyt.test import FytTestCase


class GraderViewsTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.init_old_trips_year()
        self.make_user()
        self.grader = Grader.objects.from_user(self.make_grader())

    def test_with_statistics_only_returns_graders(self):
        mommy.make(Score, trips_year=self.trips_year, grader=self.grader)
        self.assertQsEqual(Grader.objects.with_statistics(self.trips_year),
                           [self.grader])

    def test_with_statistics_returns_distinct_queryset(self):
        mommy.make(Score, 2, trips_year=self.trips_year, grader=self.grader)
        self.assertQsEqual(Grader.objects.with_statistics(self.trips_year),
                           [self.grader])

    def test_with_statistics_filters_trips_year(self):
        new_score = mommy.make(Score, trips_year=self.trips_year)
        old_score = mommy.make(Score, trips_year=self.old_trips_year)
        self.assertQsEqual(Grader.objects.with_statistics(self.trips_year),
                           [new_score.grader])

    def test_with_statistics_averages_only_include_scores_from_this_year(self):
        mommy.make(
            Score,
            trips_year=self.trips_year,
            grader=self.grader,
            leader_score__value=1,
            croo_score__value=2,
        )
        mommy.make(
            Score,
            trips_year=self.old_trips_year,
            grader=self.grader,
            leader_score__value=3,
            croo_score__value=4
        )
        graders = Grader.objects.with_statistics(self.trips_year)
        self.assertEqual(len(graders), 1)
        self.assertEqual(graders[0].score_count, 1)
        self.assertEqual(graders[0].avg_leader_score, 1)
        self.assertEqual(graders[0].avg_croo_score, 2)

    def test_with_statistics_score_histogram(self):
        self.make_score_values()
        mommy.make(
            Score,
            trips_year=self.trips_year,
            grader=self.grader,
            leader_score=self.V1,
            croo_score=self.V2
        )
        mommy.make(
            Score,
            trips_year=self.trips_year,
            grader=self.grader,
            leader_score=self.V4,
            croo_score=self.V4
        )
        graders = Grader.objects.with_statistics(self.trips_year)

        self.assertEqual(graders[0].leader_score_histogram, {
            self.V1: 1,
            self.V1_5: 0,
            self.V2: 0,
            self.V2_5: 0,
            self.V3: 0,
            self.V3_5: 0,
            self.V4: 1,
            self.V4_5: 0,
            self.V5: 0,
        })
        self.assertEqual(graders[0].croo_score_histogram, {
            self.V1: 0,
            self.V1_5: 0,
            self.V2: 1,
            self.V2_5: 0,
            self.V3: 0,
            self.V3_5: 0,
            self.V4: 1,
            self.V4_5: 0,
            self.V5: 0,
        })
