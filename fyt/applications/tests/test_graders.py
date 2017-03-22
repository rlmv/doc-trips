
from model_mommy import mommy

from fyt.applications.models import CrooApplicationGrade, LeaderApplicationGrade
from fyt.applications.views.graders import get_graders
from fyt.test import FytTestCase


class GradersDatabaseListViewTestCase(FytTestCase):

    def test_get_graders_returns_only_people_who_have_submitted_grades(self):
        trips_year = self.init_current_trips_year()
        grade = mommy.make(CrooApplicationGrade, trips_year=trips_year)
        grader = grade.grader
        random_other_user = self.mock_user()
        graders = get_graders(trips_year)
        self.assertIn(grader, graders)
        self.assertNotIn(random_other_user, graders)

    def test_get_graders_returns_distinct_queryset(self):
        trips_year = self.init_current_trips_year()
        grader = self.mock_grader()
        mommy.make(
            LeaderApplicationGrade, 2,
            trips_year=trips_year,
            grader=grader
        )
        graders = get_graders(trips_year)
        self.assertIn(grader, graders)
        self.assertEqual(len(graders), 1)

    def test_get_graders_only_returns_graders_from_this_year(self):
        trips_year = self.init_trips_year()
        old_trips_year = self.init_old_trips_year()
        grader = self.mock_grader()
        mommy.make(
            LeaderApplicationGrade,
            trips_year=old_trips_year,
            grader=grader
        )
        mommy.make(
            CrooApplicationGrade,
            trips_year=old_trips_year,
            grader=grader
        )
        self.assertEqual([], list(get_graders(trips_year)))

    def test_get_graders_avgs_only_includes_grades_from_trips_year(self):
        trips_year = self.init_trips_year()
        old_trips_year = self.init_old_trips_year()
        grader = self.mock_grader()
        mommy.make(
            LeaderApplicationGrade,
            trips_year=trips_year,
            grader=grader, grade=1
        )
        mommy.make(
            LeaderApplicationGrade,
            trips_year=old_trips_year,
            grader=grader, grade=2
        )
        mommy.make(
            CrooApplicationGrade,
            trips_year=trips_year,
            grader=grader, grade=1
        )
        mommy.make(
            CrooApplicationGrade,
            trips_year=old_trips_year,
            grader=grader, grade=2
        )
        graders = get_graders(trips_year)
        self.assertEqual(len(graders), 1)
        self.assertEqual(graders[0].leader_grade_count, 1)
        self.assertEqual(graders[0].avg_leader_grade, 1)
        self.assertEqual(graders[0].croo_grade_count, 1)
        self.assertEqual(graders[0].avg_croo_grade, 1)
