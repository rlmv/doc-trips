import unittest
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from model_mommy import mommy

from ..forms import SKIP, ScoreForm, ScoreQuestionFormset
from ..models import (
    Grader,
    Question,
    Score,
    ScoreClaim,
    ScoreQuestion,
    Volunteer,
)
from ..views.scoring import SHOW_SCORE_AVG_INTERVAL
from . import ApplicationTestMixin

from fyt.test import FytTestCase
from fyt.users.models import DartmouthUser


def _get_grader(user):
    return Grader.objects.from_user(user)


def _expire_claim(claim):
    claim.claimed_at = timezone.now() - (1.1 * ScoreClaim.HOLD_DURATION)
    claim.save()
    return claim


class ScoreModelTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()

    def test_create_score_saves_croo_head_status(self):
        app = self.make_application(trips_year=self.trips_year)
        score = Score.objects.create(
            trips_year=app.trips_year,
            application=app,
            grader=mommy.make(Grader),  # Not a croo head
            leader_score=3,
            croo_score=4)
        self.assertFalse(score.croo_head)

        score = Score.objects.create(
            trips_year=app.trips_year,
            application=app,
            grader=_get_grader(self.make_croo_head()),  # Croo head
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
                score = mommy.make(Grader).add_score(
                    application=application,
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
                score = mommy.make(Grader).add_score(
                    application=application,
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
        self.grader = _get_grader(self.make_grader())

    def test_score_form(self):
        application = self.make_application()
        form = ScoreForm(application=application, grader=self.grader)
        self.assertEqual(form.instance.application, application)

    def test_non_leader_application_does_not_have_leader_score_field(self):
        application = self.make_application(leader_willing=False)
        form = ScoreForm(application=application, grader=self.grader)
        self.assertNotIn('leader_score', form.fields)

    def test_non_croo_application_does_not_have_croo_score_field(self):
        application = self.make_application(croo_willing=False)
        form = ScoreForm(application=application, grader=self.grader)
        self.assertNotIn('croo_score', form.fields)


class ScoreClaimModelTestCase(ApplicationTestMixin, FytTestCase):

    @unittest.mock.patch('fyt.applications.models.timezone.now',
                         return_value=timezone.now())
    def test_time_left(self, patched_now):
        now = patched_now()
        claim = mommy.make(ScoreClaim)

        claim.claimed_at = now - ScoreClaim.HOLD_DURATION + timedelta(minutes=10)
        self.assertEqual(claim.time_left(), 10 * 60)

    def test_active_claims(self):
        grader = _get_grader(self.make_grader())
        active = mommy.make(ScoreClaim)
        expired = _expire_claim(mommy.make(ScoreClaim))
        scored = mommy.make(ScoreClaim, grader=grader)
        grader.add_score(scored.application)
        skipped = mommy.make(ScoreClaim, grader=grader)
        grader.skip(skipped.application)

        self.assertQsEqual(ScoreClaim.objects.active(), [active])


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

    @unittest.mock.patch('fyt.applications.models.timezone.now',
                         return_value=timezone.now())
    def test_claim_score_updates_timestamp(self, patched_now):
        now = patched_now()
        app = self.make_application()
        claim = _expire_claim(self.grader.claim_score(app))

        # Claim it again
        self.grader.claim_score(claim.application)
        claim.refresh_from_db()
        self.assertEqual(claim.claimed_at, now)

    def test_claim_adds_croo_head_status(self):
        app = self.make_application()
        grader_claim = self.grader.claim_score(app)
        self.assertFalse(grader_claim.croo_head)

        croo_head_claim = self.croo_head.claim_score(app)
        self.assertTrue(croo_head_claim.croo_head)

    def test_current_claim(self):
        app = self.make_application()
        claim = self.grader.claim_score(app)
        self.assertEqual(self.grader.current_claim(), claim)

        _expire_claim(claim)
        self.assertIsNone(self.grader.current_claim())

    def test_current_claim_ignores_already_scored(self):
        app = self.make_application()
        claim = self.grader.claim_score(app)
        self.grader.add_score(app)
        self.assertIsNone(self.grader.current_claim())

    def test_current_claim_ignores_already_skipped(self):
        app = self.make_application()
        claim = self.grader.claim_score(app)
        self.grader.skip(app)
        self.assertIsNone(self.grader.current_claim())

    def test_active_claim(self):
        app = self.make_application()
        self.assertIsNone(self.grader.active_claim(app))
        claim = self.grader.claim_score(app)
        self.assertEqual(self.grader.active_claim(app), claim)

        _expire_claim(claim)
        self.assertIsNone(self.grader.active_claim(app))

    def test_claim_next_to_score_marks_a_claim(self):
        app = self.make_application()
        self.assertEqual(self.grader.claim_next_to_score(), app)
        self.assertEqual(self.grader.current_claim().application, app)

    def test_claim_next_to_score_returns_previously_claimed_application(self):
        app1 = self.make_application(trips_year=self.trips_year)
        app2 = self.make_application(trips_year=self.trips_year)
        claim = self.grader.claim_score(app1)
        claim.claimed_at = orig_claim_time = (
            claim.claimed_at - ScoreClaim.HOLD_DURATION / 2)
        claim.save()

        self.assertEqual(app1, self.grader.claim_next_to_score())

        # And updates the claimed_at time
        claim.refresh_from_db()
        self.assertNotEqual(claim.claimed_at, orig_claim_time)

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

    def test_dont_score_apps_that_still_have_a_deadline_extension(self):
        app1 = self.make_application(
            deadline_extension=(timezone.now() + timedelta(1)))
        self.assertIsNone(self.user.next_to_score())

        # Past the extension
        app2 = self.make_application(
            deadline_extension=(timezone.now() + timedelta(-1)))
        self.assertEqual(app2, self.user.next_to_score())

    def test_user_only_scores_application_once(self):
        app = self.make_application()
        self.user.add_score(app, 4, 3)
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
        app = self.make_application(croo_willing=False)
        self.make_scores(app, Volunteer.NUM_SCORES - 1)
        claim = self.grader.claim_score(app)

        self.assertIsNone(self.user.next_to_score())
        self.assertIsNone(self.director.next_to_score())
        self.assertIsNone(self.croo_head.next_to_score())

        _expire_claim(claim)

        self.assertEqual(self.user.next_to_score(), app)
        self.assertEqual(self.director.next_to_score(), app)
        self.assertEqual(self.croo_head.next_to_score(), app)

    def test_dont_double_count_claim_and_subsequent_score(self):
        app = self.make_application(croo_willing=False)
        self.make_scores(app, Volunteer.NUM_SCORES - 2)
        claim = self.grader.claim_score(app)
        self.grader.add_score(app, 3, 4)

        self.assertEqual(self.user.next_to_score(), app)

    def test_dont_reserve_score_for_skipped_claim(self):
        app = self.make_application(croo_willing=False)
        self.make_scores(app, Volunteer.NUM_SCORES - 1)
        claim = self.grader.claim_score(app)
        self.grader.skip(app)

        self.assertEqual(self.user.next_to_score(), app)

    def test_skip_application(self):
        app = self.make_application()
        self.user.skip(app)
        self.assertIsNone(self.user.next_to_score())

    def test_reserve_one_score_for_croo_heads(self):
        app = self.make_application()
        self.make_scores(app, Volunteer.NUM_SCORES - 2)
        self.grader.claim_score(app)

        self.assertIsNone(self.user.next_to_score())
        self.assertEqual(app, self.croo_head.next_to_score())

    def test_croo_head_claim_is_as_good_as_a_score(self):
        app = self.make_application()
        self.make_scores(app, Volunteer.NUM_SCORES - 2)
        self.croo_head.claim_score(app)

        self.assertEqual(app, self.user.next_to_score())

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
        score = mommy.make(Score, application=app1)
        score.croo_head = True
        score.save()

        # Claimed croo app
        app2 = self.make_application()
        score_claim = mommy.make(ScoreClaim, application=app2)
        score_claim.croo_head = True
        score_claim.claimed_at = timezone.now()
        score_claim.save()

        # Unscored leader app - should be prefered because it has fewer
        # scores and no more croo apps require croo head scores.
        app3 = self.make_application(croo_willing=False)

        self.assertEqual(app3, self.croo_head.next_to_score())

    def test_expired_croo_head_claim(self):
        app = self.make_application()
        self.make_scores(app, Volunteer.NUM_SCORES - 1)

        # Expired
        claim = mommy.make(ScoreClaim, application=app)
        claim.croo_head = True
        _expire_claim(claim)

        # The remaining score is reserved for a croo head
        self.assertIsNone(self.user.next_to_score())
        self.assertEqual(app, self.croo_head.next_to_score())

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
        score_question = mommy.make(ScoreQuestion, trips_year=self.trips_year, pk=1)

        url = reverse('applications:score:next')
        resp = self.app.get(url, user=self.grader).follow()
        resp.form['leader_score'] = 3
        resp.form['croo_score'] = 4
        resp.form['score_question_1'] = 'A comment'
        resp.form['general'] = 'A comment about the whole'
        resp = resp.form.submit()

        self.assertEqual(len(app.scores.all()), 1)
        score = app.scores.first()
        self.assertEqual(score.leader_score, 3)
        self.assertEqual(score.croo_score, 4)
        self.assertEqual(score.grader, self.grader)
        self.assertEqual(score.application, app)
        self.assertEqual(score.trips_year, self.trips_year)
        self.assertEqual(len(score.scorecomment_set.all()), 1)
        self.assertEqual(score.scorecomment_set.first().comment, 'A comment')

        resp = self.app.get(url, user=self.grader).follow()
        self.assertTemplateUsed(resp, self.no_applications)

    def test_cant_GET_score_application_with_expired_claim(self):
        app = self.make_application(trips_year=self.trips_year)
        grader = _get_grader(self.grader)
        url = reverse('applications:score:next')

        resp = self.app.get(url, user=grader).follow()

        _expire_claim(grader.current_claim())

        resp = self.app.get(
            reverse('applications:score:add', kwargs={'pk': app.pk}),
            user=grader)
        self.assertEqual(resp.location, url)
        resp = resp.maybe_follow()

        # Shows message?
        messages = list(resp.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('You took longer than the alloted time', messages[0].message)

    def test_cant_POST_score_application_with_expired_claim(self):
        app = self.make_application(trips_year=self.trips_year)
        grader = _get_grader(self.grader)
        url = reverse('applications:score:next')

        # POST
        resp = self.app.get(url, user=grader).follow()
        _expire_claim(grader.current_claim())

        resp.form['leader_score'] = 3
        resp.form['croo_score'] = 4
        resp.form['general'] = 'A comment about the whole'
        resp = resp.form.submit().maybe_follow()

        # Shows message?
        messages = list(resp.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('You took longer than the alloted time', messages[0].message)

        # Score not recorded
        self.assertEqual(Score.objects.filter(grader=grader).count(), 0)

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
        grader = _get_grader(self.grader)
        for i in range(SHOW_SCORE_AVG_INTERVAL):
            mommy.make(
                Score,
                trips_year=self.trips_year,
                grader=grader,
                leader_score=3,
                croo_score=4
            )

        url = reverse('applications:score:next')
        resp = self.app.get(url, user=grader).follow()

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


class ScoreQuestionFormsetTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()

    def test_formset_save(self):
        formset = ScoreQuestionFormset(
            prefix='formset',
            trips_year=self.trips_year,
            data={
                'formset-INITIAL_FORMS': '0',
                'formset-TOTAL_FORMS': '3',
                'formset-MIN_NUM_FORMS': '',
                'formset-MAX_NUM_FORMS': '',
                'formset-0-question': 'What is your name?',
                'formset-0-order': '3',
            })
        self.assertTrue(formset.is_valid())
        formset.save()
        question = ScoreQuestion.objects.get()
        self.assertEqual(question.question, 'What is your name?')
        self.assertEqual(question.order, 3)
        self.assertEqual(question.trips_year, self.trips_year)
