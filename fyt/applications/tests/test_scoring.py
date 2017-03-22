
from django.core.urlresolvers import reverse
from model_mommy import mommy

from ..models import Score, Volunteer
from . import ApplicationTestMixin

from fyt.applications.views.scoring import SHOW_SCORE_AVG_INTERVAL, SKIP
from fyt.test import FytTestCase


class ScoreModelTestCase(ApplicationTestMixin, FytTestCase):

    def test_create_score_saves_croo_head_status(self):
        self.init_trips_year()
        app = self.make_application(trips_year=self.trips_year)

        score = Score.objects.create(
            trips_year=app.trips_year,
            application=app,
            grader=self.make_user(),  # Not a croo head
            score=3)
        self.assertFalse(score.croo_head)

        score = Score.objects.create(
            trips_year=app.trips_year,
            application=app,
            grader=self.make_croo_head(),  # Croo head
            score=3)
        self.assertTrue(score.croo_head)


class VolunteerManagerTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.make_user()
        self.make_director()
        self.make_directorate()
        self.make_croo_head()

    def make_scores(self, app, n):
        for i in range(n):
            mommy.make(Score, trips_year=self.trips_year, application=app)

    def test_only_score_apps_for_this_year(self):
        last_year = self.init_old_trips_year()

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
        self.make_scores(app, Volunteer.NUM_SCORES)

        self.assertIsNone(Volunteer.objects.next_to_score(self.user))
        self.assertIsNone(Volunteer.objects.next_to_score(self.director))

    def test_skip_application(self):
        app = self.make_application()
        app.skip(self.user)
        self.assertIsNone(Volunteer.objects.next_to_score(self.user))

    def test_reserve_one_score_for_croo_heads(self):
        app = self.make_application()
        self.make_scores(app, Volunteer.NUM_SCORES - 1)

        self.assertIsNone(Volunteer.objects.next_to_score(self.user))
        self.assertEqual(app, Volunteer.objects.next_to_score(self.croo_head))

    def test_dont_reserve_croo_head_scores_for_leader_applications(self):
        app = self.make_application(croo_willing=False)
        self.make_scores(app, Volunteer.NUM_SCORES - 1)

        self.assertEqual(app, Volunteer.objects.next_to_score(self.user))
        self.assertEqual(app, Volunteer.objects.next_to_score(self.director))
        self.assertEqual(app, Volunteer.objects.next_to_score(self.directorate))
        self.assertEqual(app, Volunteer.objects.next_to_score(self.croo_head))

    def test_croo_heads_prefer_croo_apps(self):
        app1 = self.make_application(croo_willing=False)  # Leader only
        app2 = self.make_application()

        self.assertEqual(app2, Volunteer.objects.next_to_score(self.croo_head))


class ScoreViewsTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.make_director()
        self.make_grader()
        self.make_user()

    score_urls = [
        reverse('applications:score:next'),
        reverse('applications:score:no_applications_left'),
    ]

    not_available = 'applications/scoring_not_available.html'
    no_applications = 'applications/no_applications.html'

    def test_cant_score_before_application_deadline(self):
        self.open_application()
        for url in self.score_urls:
            resp = self.app.get(url, user=self.director).maybe_follow()
            self.assertTemplateUsed(resp, self.not_available)

    def test_can_score_after_application_deadline(self):
        self.close_application()
        for url in self.score_urls:
            resp = self.app.get(url, user=self.director).maybe_follow()
            self.assertTemplateNotUsed(resp, self.not_available)

    def test_scoring_permissions(self):
        self.close_application()
        for url in self.score_urls + [reverse('applications:score:scoring')]:
            self.app.get(url, user=self.director)
            self.app.get(url, user=self.user, status=403)

    def test_score_application(self):
        self.close_application()
        app = self.make_application(trips_year=self.trips_year)

        url = reverse('applications:score:next')
        resp = self.app.get(url, user=self.grader).follow()
        resp.form['score'] = 3
        resp = resp.form.submit()

        self.assertEqual(len(app.scores.all()), 1)
        score = app.scores.first()
        self.assertEqual(score.score, 3)
        self.assertEqual(score.grader, self.grader)
        self.assertEqual(score.application, app)
        self.assertEqual(score.trips_year, self.trips_year)

    def test_skip_application(self):
        self.close_application()
        app = self.make_application(trips_year=self.trips_year)

        url = reverse('applications:score:next')
        resp = self.app.get(url, user=self.grader).follow()
        resp.form.submit(SKIP)

        self.assertEqual(len(app.skips.all()), 1)
        skip = app.skips.first()
        self.assertEqual(skip.grader, self.grader)
        self.assertEqual(skip.application, app)
        self.assertEqual(skip.trips_year, self.trips_year)

        resp = self.app.get(url, user=self.grader).follow()
        self.assertTemplateUsed(resp, self.no_applications)

    def test_show_average_grade_in_messages(self):
        self.close_application()
        self.make_application(trips_year=self.trips_year)

        for i in range(SHOW_SCORE_AVG_INTERVAL):
            mommy.make(
                Score,
                trips_year=self.trips_year,
                grader=self.grader,
                score=3
            )

        url = reverse('applications:score:next')
        resp = self.app.get(url, user=self.grader).follow()

        messages = list(resp.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('average awarded score is 3', messages[0].message)

    def test_delete_score_is_restricted_to_directors(self):
        score = mommy.make(Score, trips_year=self.trips_year)
        url = reverse('db:score:delete', kwargs={'trips_year': self.trips_year, 'pk': score.pk})
        res = self.app.get(url, user=self.make_tlt(), status=403)
        res = self.app.get(url, user=self.make_directorate(), status=403)
        res = self.app.get(url, user=self.grader, status=403)
        res = self.app.get(url, user=self.user, status=403)
        res = self.app.get(url, user=self.director)

    def test_delete_score_redirects_to_app(self):
        application = self.make_application(self.trips_year)
        score = mommy.make(Score, trips_year=self.trips_year, application=application)
        url = reverse('db:score:delete', kwargs={'trips_year': self.trips_year, 'pk': score.pk})
        resp = self.app.get(url, user=self.director)
        resp = resp.form.submit()
        self.assertRedirects(resp, application.detail_url())
