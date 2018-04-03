import unittest

from django.core.exceptions import ValidationError
from django.urls import reverse
from model_mommy import mommy

from ..models import Grader, Score, ScoreClaim, Volunteer, Question
from ..views.scoring import SHOW_SCORE_AVG_INTERVAL
from ..forms import ScoreForm, SKIP
from . import ApplicationTestMixin

from fyt.test import FytTestCase
from fyt.users.models import DartmouthUser


class ScoreModelTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()

    def test_create_score_saves_croo_head_status(self):
        app = self.make_application(trips_year=self.trips_year)

        score = Score.objects.create(
            trips_year=app.trips_year,
            application=app,
            grader=self.make_user(),  # Not a croo head
            leader_score=3,
            croo_score=4)
        self.assertFalse(score.croo_head)

        score = Score.objects.create(
            trips_year=app.trips_year,
            application=app,
            grader=self.make_croo_head(),  # Croo head
            leader_score=3,
            croo_score=4)
        self.assertTrue(score.croo_head)

    def test_leader_application_requires_leader_score(self):
        for leader_willing, leader_score, ok in [
                [True, 3, True],
                [True, None, False],
                [False, 3, True],
                [False, None, True]]:

            def _check():
                application = self.make_application(
                    trips_year=self.trips_year,
                    leader_willing=leader_willing,
                    croo_willing=False)
                score = application.add_score(
                    grader=mommy.make(DartmouthUser),
                    leader_score=leader_score,
                    general="A comment")
                score.full_clean()

            if ok:
                _check()
            else:
                with self.assertRaises(ValidationError):
                    _check()

    def test_croo_application_requires_croo_score(self):
        for croo_willing, croo_score, ok in [
                [True, 3, True],
                [True, None, False],
                [False, 3, True],
                [False, None, True]]:

            def _check():
                application = self.make_application(
                    trips_year=self.trips_year,
                    leader_willing=False,
                    croo_willing=croo_willing)
                score = application.add_score(
                    grader=mommy.make(DartmouthUser),
                    croo_score=croo_score,
                    general="A comment")
                score.full_clean()

            if ok:
                _check()
            else:
                with self.assertRaises(ValidationError):
                    _check()


class ScoreFormTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()

    def test_score_form(self):
        application = self.make_application()
        form = ScoreForm(application=application)
        self.assertEqual(form.instance.application, application)

    def test_non_leader_application_does_not_have_leader_score_field(self):
        application = self.make_application(leader_willing=False)
        form = ScoreForm(application=application)
        self.assertNotIn('leader_score', form.fields)

    def test_non_croo_application_does_not_have_croo_score_field(self):
        application = self.make_application(croo_willing=False)
        form = ScoreForm(application=application)
        self.assertNotIn('croo_score', form.fields)


def _get_grader(user):
    return Grader.objects.from_user(user)


class GraderModelTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.init_old_trips_year()
        # Convert the normal users to Graders
        self.user = _get_grader(self.make_user())
        self.grader = _get_grader(self.make_grader())
        self.director = _get_grader(self.make_director())
        self.directorate = _get_grader(self.make_directorate())
        self.croo_head = _get_grader(self.make_croo_head())

    def make_scores(self, app, n):
        for i in range(n):
            mommy.make(Score, croo_head=False, trips_year=self.trips_year,
                       application=app)

    def test_convert_grader_to_user(self):
        _user = mommy.make(DartmouthUser)
        _grader = Grader.objects.from_user(_user)
        self.assertEqual(_user.pk, _grader.pk)

    def test_is_croo_head(self):
        self.assertFalse(self.grader.is_croo_head)
        self.assertTrue(self.croo_head.is_croo_head)

    def test_average_score_methods(self):
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
            leader_score=3,
            croo_score=5,
        )
        mommy.make(
            Score,
            trips_year=self.old_trips_year,
            grader=self.grader,
            leader_score=3,
            croo_score=4
        )
        self.assertEqual(self.grader.avg_leader_score(self.trips_year), 2)
        self.assertEqual(self.grader.avg_croo_score(self.trips_year), 3.5)
        self.assertEqual(self.grader.score_count(self.trips_year), 2)

    def test_claim_score(self):
        app = self.make_application()
        self.grader.claim_score(app)
        claim = ScoreClaim.objects.get()
        self.assertEqual(claim.grader, self.grader)
        self.assertEqual(claim.application, app)
        self.assertEqual(claim.trips_year, self.trips_year)
        self.assertIsNotNone(claim.claimed_at)

    def test_current_claim(self):
        app = self.make_application()
        claim = self.grader.claim_score(app)
        self.assertEqual(self.grader.current_claim(), claim)

        # Expired
        claim.claimed_at = claim.claimed_at - 1.1 * ScoreClaim.HOLD_DURATION
        claim.save()

        self.assertIsNone(self.grader.current_claim())

    def test_current_claim_ignores_already_scored(self):
        app = self.make_application()
        claim = self.grader.claim_score(app)
        app.add_score(self.grader)
        self.assertIsNone(self.grader.current_claim())

    def test_claim_next_to_score_marks_a_claim(self):
        app = self.make_application()
        self.assertEqual(self.grader.claim_next_to_score(), app)
        self.assertEqual(self.grader.current_claim().application, app)

    def test_claim_next_to_score_returns_previously_claimed_application(self):
        app1 = self.make_application(trips_year=self.trips_year)
        app2 = self.make_application(trips_year=self.trips_year)
        self.grader.claim_score(app1)
        self.assertEqual(app1, self.grader.claim_next_to_score())

    def test_claim_next_to_score_with_no_remaining_applications(self):
        self.assertIsNone(self.grader.claim_next_to_score())

    # ------ next_to_score logic -------

    def test_only_score_apps_for_this_year(self):
        last_year = self.init_old_trips_year()
        app1 = self.make_application(trips_year=self.trips_year)
        app2 = self.make_application(trips_year=last_year)
        self.assertEqual(app1, self.user.next_to_score())

    def test_only_score_complete_apps(self):
        self.make_application(leader_willing=False, croo_willing=False)
        self.assertIsNone(self.user.next_to_score())

    def test_user_only_scores_application_once(self):
        app = self.make_application()
        app.add_score(self.user, 4, 3)
        self.assertIsNone(self.user.next_to_score())

    def test_only_score_pending_applications(self):
        app = self.make_application()  # PENDING
        for status, _ in Volunteer.STATUS_CHOICES:
            if status != Volunteer.PENDING:
                self.make_application(status=status)

        self.assertEqual(app, self.user.next_to_score())

    def test_only_score_3_times(self):
        app = self.make_application()
        self.make_scores(app, Volunteer.NUM_SCORES)

        self.assertIsNone(self.user.next_to_score())
        self.assertIsNone(self.director.next_to_score())
        self.assertIsNone(self.croo_head.next_to_score())

    def test_active_claims_contribute_to_score_count(self):
        app = self.make_application()
        self.make_scores(app, Volunteer.NUM_SCORES - 1)
        claim = self.grader.claim_score(app)

        self.assertIsNone(self.user.next_to_score())
        self.assertIsNone(self.director.next_to_score())
        self.assertIsNone(self.croo_head.next_to_score())

        # Expired
        claim.claimed_at = claim.claimed_at - 1.1 * ScoreClaim.HOLD_DURATION
        claim.save()

        self.assertEqual(self.user.next_to_score(), app)
        self.assertEqual(self.director.next_to_score(), app)
        self.assertEqual(self.croo_head.next_to_score(), app)

    def test_skip_application(self):
        app = self.make_application()
        app.skip(self.user)
        self.assertIsNone(self.user.next_to_score())

    @unittest.expectedFailure
    def test_reserve_one_score_for_croo_heads(self):
        app = self.make_application()
        self.make_scores(app, Volunteer.NUM_SCORES - 1)

        self.assertIsNone(self.user.next_to_score())
        self.assertEqual(app, self.croo_head.next_to_score())

    def test_dont_reserve_croo_head_scores_for_leader_applications(self):
        app = self.make_application(croo_willing=False)
        self.make_scores(app, Volunteer.NUM_SCORES - 1)

        self.assertEqual(app, self.user.next_to_score())
        self.assertEqual(app, self.director.next_to_score())
        self.assertEqual(app, self.directorate.next_to_score())
        self.assertEqual(app, self.croo_head.next_to_score())

    def test_croo_heads_prefer_croo_apps(self):
        app1 = self.make_application(croo_willing=False)  # Leader only
        app2 = self.make_application()

        self.assertEqual(app2, self.croo_head.next_to_score())

    def test_prefer_apps_with_fewer_scores(self):
        app1 = self.make_application()
        app2 = self.make_application()
        app3 = self.make_application()
        self.make_scores(app2, 1)
        self.grader.claim_score(app3)
        self.assertEqual(app1, self.director.next_to_score())

    def test_wtf_query(self):
        # Scored croo app
        app1 = self.make_application()
        self.make_scores(app1, 1)
        mommy.make(Score, application=app1, leader_score=3, croo_score=4,
                   croo_head=True)

        # Unscored leader app - should be prefered because it has fewer
        # scores and no more croo apps required croo head scores.
        app2 = self.make_application(croo_willing=False)

        self.assertEqual(app2, self.croo_head.next_to_score())

    def test_score_progress(self):
        # 1/3 scores
        app1 = self.make_application()
        self.make_scores(app1, 1)

        # 10/3 scores becomes 3/3
        app2 = self.make_application()
        self.make_scores(app2, 10)

        # 0/3 scores
        app3 = self.make_application()

        progress = {
            'complete': 4,
            'total': 9,
            'percentage': 44
        }
        self.assertEqual(progress, Volunteer.objects.score_progress(self.trips_year))

    def test_score_progress_with_no_scores(self):
        # Don't divide by zero
        progress = {
            'complete': 0,
            'total': 0,
            'percentage': 100
        }
        self.assertEqual(progress, Volunteer.objects.score_progress(self.trips_year))


class ScoreViewsTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.make_director()
        self.make_grader()
        self.make_user()
        self.open_scoring()

    score_urls = [
        reverse('applications:score:next'),
        reverse('applications:score:no_applications_left'),
    ]

    not_available = 'applications/scoring_not_available.html'
    no_applications = 'applications/no_applications.html'

    def test_scoring_availability(self):
        self.close_scoring()
        for url in self.score_urls:
            resp = self.app.get(url, user=self.director).maybe_follow()
            self.assertTemplateUsed(resp, self.not_available)

        self.open_scoring()
        for url in self.score_urls:
            resp = self.app.get(url, user=self.director).maybe_follow()
            self.assertTemplateNotUsed(resp, self.not_available)

    def test_scoring_permissions(self):
        for url in self.score_urls + [reverse('applications:score:scoring')]:
            self.app.get(url, user=self.director)
            self.app.get(url, user=self.user, status=403)

    def test_score_application(self):
        app = self.make_application(trips_year=self.trips_year)
        question = mommy.make(Question, trips_year=self.trips_year, type=Question.ALL)
        app.answer_question(question, "An answer")

        url = reverse('applications:score:next')
        resp = self.app.get(url, user=self.grader).follow()
        resp.form['leader_score'] = 3
        resp.form['croo_score'] = 4
        resp.form['answer_1'] = 'A comment'
        resp.form['general'] = 'A comment about the whole'
        resp = resp.form.submit()

        self.assertEqual(len(app.scores.all()), 1)
        score = app.scores.first()
        self.assertEqual(score.leader_score, 3)
        self.assertEqual(score.croo_score, 4)
        self.assertEqual(score.grader, self.grader)
        self.assertEqual(score.application, app)
        self.assertEqual(score.trips_year, self.trips_year)
        self.assertEqual(len(score.answercomment_set.all()), 1)
        self.assertEqual(score.answercomment_set.first().comment, 'A comment')

    def test_skip_application(self):
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
        self.make_application(trips_year=self.trips_year)

        for i in range(SHOW_SCORE_AVG_INTERVAL):
            mommy.make(
                Score,
                trips_year=self.trips_year,
                grader=self.grader,
                leader_score=3,
                croo_score=4
            )

        url = reverse('applications:score:next')
        resp = self.app.get(url, user=self.grader).follow()

        messages = list(resp.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('average awarded leader score is 3.0', messages[0].message)
        self.assertIn('average awarded croo score is 4.0', messages[0].message)

    def test_delete_score_is_restricted_to_directors(self):
        score = mommy.make(Score, trips_year=self.trips_year)
        url = reverse('core:score:delete', kwargs={'trips_year': self.trips_year, 'pk': score.pk})
        res = self.app.get(url, user=self.make_tlt(), status=403)
        res = self.app.get(url, user=self.make_directorate(), status=403)
        res = self.app.get(url, user=self.grader, status=403)
        res = self.app.get(url, user=self.user, status=403)
        res = self.app.get(url, user=self.director)

    def test_delete_score_redirects_to_app(self):
        application = self.make_application(self.trips_year)
        score = mommy.make(Score, trips_year=self.trips_year, application=application)
        url = reverse('core:score:delete', kwargs={'trips_year': self.trips_year, 'pk': score.pk})
        resp = self.app.get(url, user=self.director)
        resp = resp.form.submit()
        self.assertRedirects(resp, application.detail_url())
