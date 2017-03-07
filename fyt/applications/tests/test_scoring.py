
from model_mommy import mommy

from . import ApplicationTestMixin
from ..models import Volunteer, Score, Skip
from fyt.test import FytTestCase


class VolunteerManagerTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.user = self.mock_user()

    def test_only_score_apps_for_this_year(self):
        last_year = self.init_previous_trips_year()

        app1 = self.make_application(trips_year=self.trips_year)
        app2 = self.make_application(trips_year=last_year)

        self.assertEqual(app1, Volunteer.objects.next_to_score(self.user))

    def test_only_score_complete_apps(self):
        self.make_application(leader_willing=False, croo_willing=False)
        self.assertIsNone(Volunteer.objects.next_to_score(self.user))

    def test_user_only_scores_application_once(self):
        app = self.make_application()
        app.add_score(self.user, 4)
        self.assertIsNone(Volunteer.objects.next_to_score(self.user))

    def test_only_score_pending_applications(self):
        app = self.make_application()  # PENDING
        for status, _ in Volunteer.STATUS_CHOICES:
            if status != Volunteer.PENDING:
                self.make_application(status=status)

        self.assertEqual(app, Volunteer.objects.next_to_score(self.user))

    def test_only_score_3_times(self):
        app = self.make_application()
        for i in range(Volunteer.NUM_SCORES):
            mommy.make(Score, trips_year=self.trips_year, application=app)
            
        self.assertIsNone(Volunteer.objects.next_to_score(self.user))
