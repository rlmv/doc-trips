from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from model_mommy import mommy

from ..forms import ApplicationAdminForm, LeaderSupplementForm, QuestionForm, AgreementForm
from ..models import (
    Answer,
    ApplicationInformation,
    CrooSupplement,
    Grader,
    LeaderSupplement,
    PortalContent,
    Question,
    ScoreValue,
    Volunteer,
    validate_class_year,
)

from fyt.croos.models import Croo
from fyt.test import FytTestCase
from fyt.timetable.models import Timetable
from fyt.training.models import FirstAidCertification
from fyt.trips.models import Section, Trip, TripType
from fyt.users.models import DartmouthUser
from fyt.utils.choices import AVAILABLE, PREFER


def make_application(
    status=Volunteer.PENDING,
    trips_year=None,
    trip_assignment=None,
    croo_assignment=None,
    leader_willing=True,
    croo_willing=True,
    **kwargs
):

    application = mommy.make(
        Volunteer,
        status=status,
        trips_year=trips_year,
        trip_assignment=trip_assignment,
        croo_assignment=croo_assignment,
        leader_willing=leader_willing,
        croo_willing=croo_willing,
        **kwargs
    )

    leader_app = mommy.make(
        LeaderSupplement, application=application, trips_year=trips_year
    )

    croo_app = mommy.make(
        CrooSupplement, application=application, trips_year=trips_year
    )

    return application


class ApplicationTestMixin:

    """ Common utilities for testing applications """

    def _timetable(self):
        try:
            return Timetable.objects.timetable()
        except Timetable.DoesNotExist:
            return Timetable()

    def open_application(self):
        """" open leader applications """
        t = self._timetable()
        t.applications_open = timezone.now() + timedelta(-1)
        t.applications_close = timezone.now() + timedelta(1)
        t.save()

    def close_application(self):
        """ close leader applications """
        t = self._timetable()
        t.applications_open = timezone.now() + timedelta(-2)
        t.applications_close = timezone.now() + timedelta(-1)
        t.save()

    def open_scoring(self):
        t = self._timetable()
        t.scoring_available = True
        t.save()

    def close_scoring(self):
        t = self._timetable()
        t.scoring_available = False
        t.save()

    def make_application(self, trips_year=None, **kwargs):
        if trips_year is None:
            trips_year = self.trips_year
        return make_application(trips_year=trips_year, **kwargs)

    def make_score_values(self, trips_year=None):
        if trips_year is None:
            trips_year = self.trips_year

        # TODO: use bulk_create
        for i in [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]:
            name = "V{}".format(str(i).replace('.', '_'))
            value = ScoreValue.objects.create(
                trips_year=trips_year, value=i, description=""
            )
            setattr(self, name, value)


class VolunteerModelTestCase(ApplicationTestMixin, FytTestCase):
    def test_must_be_LEADER_to_be_trip_assignment(self):
        trips_year = self.init_trips_year()
        for status in ['PENDING', 'LEADER_WAITLIST', 'CROO', 'REJECTED', 'CANCELED']:
            application = mommy.make(
                Volunteer,
                status=getattr(Volunteer, status),
                trips_year=trips_year,
                trippee_confidentiality=True,
                in_goodstanding_with_college=True,
                trainings=True,
            )
            application.trip_assignment = mommy.make(Trip, trips_year=trips_year)
            with self.assertRaises(ValidationError):
                application.full_clean()

        application.status = Volunteer.LEADER
        application.full_clean()

    def test_must_be_CROO_to_be_croo_assignment(self):
        trips_year = self.init_trips_year()
        for status in ['PENDING', 'LEADER_WAITLIST', 'LEADER', 'REJECTED', 'CANCELED']:
            application = mommy.make(
                Volunteer,
                status=getattr(Volunteer, status),
                trips_year=trips_year,
                trippee_confidentiality=True,
                in_goodstanding_with_college=True,
                trainings=True,
            )
            application.croo_assignment = mommy.make(Croo, trips_year=trips_year)
            with self.assertRaises(ValidationError):
                application.full_clean()

        application.status = Volunteer.CROO
        application.full_clean()

    def test_get_preferred_trips(self):
        trips_year = self.init_trips_year()
        application = self.make_application(trips_year=trips_year)
        ls = application.leader_supplement
        preferred_trip = mommy.make(Trip, trips_year=trips_year)
        ls.set_section_preference(preferred_trip.section, PREFER)
        ls.set_triptype_preference(preferred_trip.template.triptype, PREFER)
        not_preferred_trip = mommy.make(Trip, trips_year=trips_year)
        self.assertEqual([preferred_trip], list(application.get_preferred_trips()))

    def test_get_available_trips(self):
        trips_year = self.init_trips_year()
        application = self.make_application(trips_year=trips_year)
        ls = application.leader_supplement
        preferred_triptype = mommy.make(TripType, trips_year=trips_year)
        preferred_section = mommy.make(Section, trips_year=trips_year)
        available_triptype = mommy.make(TripType, trips_year=trips_year)
        available_section = mommy.make(Section, trips_year=trips_year)
        ls.set_section_preference(preferred_section, PREFER)
        ls.set_triptype_preference(preferred_triptype, PREFER)
        ls.set_section_preference(available_section, AVAILABLE)
        ls.set_triptype_preference(available_triptype, AVAILABLE)

        make = lambda s, t: mommy.make(
            Trip, trips_year=trips_year, section=s, template__triptype=t
        )
        preferred_trip = make(preferred_section, preferred_triptype)
        available_trips = [  # all other permutations
            make(preferred_section, available_triptype),
            make(available_section, preferred_triptype),
            make(available_section, available_triptype),
        ]
        not_preferred_trip = mommy.make(Trip, trips_year=trips_year)
        self.assertEqual(set(available_trips), set(application.get_available_trips()))

    def test_set_section_preference(self):
        trips_year = self.init_trips_year()
        ls = self.make_application(trips_year=trips_year).leader_supplement
        section = mommy.make(Section, trips_year=trips_year)
        ls.set_section_preference(section, PREFER)

        self.assertEqual(len(ls.leadersectionchoice_set.all()), 1)
        pref = ls.leadersectionchoice_set.first()
        self.assertEqual(pref.section, section)
        self.assertEqual(pref.preference, PREFER)

    def test_set_triptype_preference(self):
        trips_year = self.init_trips_year()
        ls = self.make_application(trips_year=trips_year).leader_supplement
        triptype = mommy.make(TripType, trips_year=trips_year)
        ls.set_triptype_preference(triptype, AVAILABLE)

        self.assertEqual(len(ls.leadertriptypechoice_set.all()), 1)
        pref = ls.leadertriptypechoice_set.first()
        self.assertEqual(pref.triptype, triptype)
        self.assertEqual(pref.preference, AVAILABLE)

    def test_leader_application_complete(self):
        trips_year = self.init_trips_year()
        question1 = mommy.make(Question, trips_year=trips_year, type=Question.ALL)
        question2 = mommy.make(Question, trips_year=trips_year, type=Question.LEADER)
        question3 = mommy.make(Question, trips_year=trips_year, type=Question.CROO)
        question4 = mommy.make(Question, trips_year=trips_year, type=Question.OPTIONAL)

        app = make_application(trips_year=trips_year)
        app.leader_willing = True

        # Not complete because there is an unanswered question
        self.assertFalse(app.leader_application_complete)

        # Not complete because the leader question is unanswered
        app.answer_question(question1, 'An answer')
        self.assertFalse(app.leader_application_complete)

        # Not complete because there is a blank answer
        answer2 = app.answer_question(question2, '')
        self.assertFalse(app.leader_application_complete)

        # Complete - answered
        answer2.answer = 'Some text!'
        answer2.save()
        self.assertTrue(app.leader_application_complete)

        # Answered but unwilling
        app.leader_willing = False
        self.assertFalse(app.leader_application_complete)

    def test_croo_application_complete(self):
        trips_year = self.init_trips_year()
        question1 = mommy.make(Question, trips_year=trips_year, type=Question.ALL)
        question2 = mommy.make(Question, trips_year=trips_year, type=Question.LEADER)
        question3 = mommy.make(Question, trips_year=trips_year, type=Question.CROO)
        question4 = mommy.make(Question, trips_year=trips_year, type=Question.OPTIONAL)

        app = make_application(trips_year=trips_year)
        app.croo_willing = True

        # Not complete because there is an unanswered question
        self.assertFalse(app.croo_application_complete)

        # Not complete because there is a blank answer
        app.answer_question(question1, 'Answer')
        self.assertFalse(app.croo_application_complete)

        # Not complete because the croo question is unanswered
        answer3 = app.answer_question(question3, '')
        self.assertFalse(app.croo_application_complete)

        # Complete - answered
        answer3.answer = 'Some text!'
        answer3.save()
        self.assertTrue(app.croo_application_complete)

        # Answered but unwilling
        app.croo_willing = False
        self.assertFalse(app.croo_application_complete)

    def test_answer_question(self):
        trips_year = self.init_trips_year()
        app = make_application(trips_year=trips_year)

        question = mommy.make(Question, trips_year=trips_year)
        app.answer_question(question, "An answer!")

        self.assertEqual(app.answer_set.count(), 1)
        answer = app.answer_set.first()
        self.assertEqual(answer.question, question)
        self.assertEqual(answer.answer, "An answer!")
        self.assertEqual(answer.application, app)

    def test_add_score(self):
        trips_year = self.init_trips_year()
        self.make_score_values()
        app = make_application(trips_year=trips_year)
        grader = mommy.make(Grader)
        grader.add_score(app, self.V3, self.V1)

        score = app.scores.first()
        self.assertEqual(score.application, app)
        self.assertEqual(score.grader, grader)
        self.assertEqual(score.leader_score, self.V3)
        self.assertEqual(score.croo_score, self.V1)
        self.assertEqual(score.trips_year, trips_year)

    def test_average_scores(self):
        trips_year = self.init_trips_year()
        self.make_score_values()
        app = make_application(trips_year=trips_year)
        mommy.make(Grader).add_score(app, self.V3, self.V1)
        mommy.make(Grader).add_score(app, self.V4, self.V2)
        mommy.make(Grader).add_score(app, None, None)
        self.assertEqual(app.average_leader_score(), 3.5)
        self.assertEqual(app.average_croo_score(), 1.5)

    def test_class_year_validation(self):
        validate_class_year(2015)
        with self.assertRaises(ValidationError):
            validate_class_year(19)
        with self.assertRaises(ValidationError):
            validate_class_year(3200)

    def test_first_aid_certification_str(self):
        trips_year = self.init_trips_year()
        application = self.make_application(trips_year=trips_year)
        cert1 = mommy.make(
            FirstAidCertification, trips_year=trips_year, volunteer=application
        )
        cert2 = mommy.make(
            FirstAidCertification, trips_year=trips_year, volunteer=application
        )
        application.refresh_from_db()
        self.assertEqual(
            application.first_aid_certifications_str(), str(cert1) + '\n' + str(cert2)
        )

    def test_first_aid_certifications_str_with_legacy_fields(self):
        trips_year = self.init_trips_year()
        application = self.make_application(trips_year=trips_year)
        application.medical_certifications = "a certification"
        application.medical_experience = "some experience"
        self.assertEqual(
            application.first_aid_certifications_str(),
            "a certification\n\nsome experience",
        )


class AnswerModelTestCase(ApplicationTestMixin, FytTestCase):
    def test_word_count_validation(self):
        trips_year = self.init_trips_year()
        question = mommy.make(Question)
        application = self.make_application(trips_year=trips_year)

        answer = Answer(question=question, application=application, answer='')
        answer.full_clean()

        answer = Answer(
            question=question, application=application, answer=('word ' * 301)
        )
        with self.assertRaises(ValidationError):
            answer.full_clean()


class QuestionModelTestCase(FytTestCase):
    def setUp(self):
        self.init_trips_year()
        self.q_general = mommy.make(
            Question, trips_year=self.trips_year, index=0, type=Question.ALL
        )
        self.q_leader = mommy.make(
            Question, trips_year=self.trips_year, index=1, type=Question.LEADER
        )
        self.q_croo = mommy.make(
            Question, trips_year=self.trips_year, index=2, type=Question.CROO
        )
        self.q_optional = mommy.make(
            Question, trips_year=self.trips_year, index=3, type=Question.OPTIONAL
        )

    def test_leader_only(self):
        self.assertFalse(self.q_general.leader_only)
        self.assertTrue(self.q_leader.leader_only)
        self.assertFalse(self.q_croo.leader_only)

    def test_croo_only(self):
        self.assertFalse(self.q_general.croo_only)
        self.assertFalse(self.q_leader.croo_only)
        self.assertTrue(self.q_croo.croo_only)

    def test_required_for_leaders(self):
        qs = Question.objects.required_for_leaders(self.trips_year)
        self.assertQsEqual(qs, [self.q_general, self.q_leader])

    def test_required_for_croos(self):
        qs = Question.objects.required_for_croos(self.trips_year)
        self.assertQsEqual(qs, [self.q_general, self.q_croo])

    def test_required_questions(self):
        qs = Question.objects.required(self.trips_year)
        self.assertQsEqual(qs, [self.q_general, self.q_leader, self.q_croo])


class ApplicationManager_prospective_leaders_TestCase(
    ApplicationTestMixin, FytTestCase
):
    def setUp(self):
        self.init_trips_year()

    def test_prospective_leader_with_preferred_choices(self):
        trip = mommy.make(Trip, trips_year=self.trips_year)

        app = self.make_application(status=Volunteer.LEADER)
        app.leader_supplement.set_section_preference(trip.section, PREFER)
        app.leader_supplement.set_triptype_preference(trip.template.triptype, PREFER)

        prospects = Volunteer.objects.prospective_leaders_for_trip(trip)
        self.assertEqual(list(prospects), [app])

    def test_prospective_leader_with_available_choices(self):
        trip = mommy.make(Trip, trips_year=self.trips_year)

        app = self.make_application(status=Volunteer.LEADER_WAITLIST)
        app.leader_supplement.set_section_preference(trip.section, AVAILABLE)
        app.leader_supplement.set_triptype_preference(trip.template.triptype, AVAILABLE)

        prospects = Volunteer.objects.prospective_leaders_for_trip(trip)
        self.assertEqual(list(prospects), [app])

    def test_only_complete_applications(self):
        trip = mommy.make(Trip, trips_year=self.trips_year)
        question = mommy.make(Question, trips_year=self.trips_year)

        prospective = self.make_application(status=Volunteer.LEADER_WAITLIST)
        prospective.answer_question(question, 'An answer')
        prospective.leader_supplement.set_section_preference(trip.section, AVAILABLE)
        prospective.leader_supplement.set_triptype_preference(
            trip.template.triptype, AVAILABLE
        )

        not_prosp = self.make_application(status=Volunteer.LEADER_WAITLIST)
        not_prosp.leader_supplement.set_section_preference(trip.section, AVAILABLE)
        not_prosp.leader_supplement.set_triptype_preference(
            trip.template.triptype, AVAILABLE
        )

        prospects = Volunteer.objects.prospective_leaders_for_trip(trip)
        self.assertEqual(list(prospects), [prospective])

    def test_without_section_preference(self):
        trip = mommy.make(Trip, trips_year=self.trips_year)

        # otherwise available
        app = self.make_application(status=Volunteer.LEADER)
        app.leader_supplement.set_triptype_preference(trip.template.triptype, PREFER)

        prospects = Volunteer.objects.prospective_leaders_for_trip(trip)
        self.assertEqual(list(prospects), [])

    def test_without_triptype_preference(self):
        trip = mommy.make(Trip, trips_year=self.trips_year)

        app = self.make_application(status=Volunteer.LEADER)
        app.leader_supplement.set_section_preference(trip.section, PREFER)

        prospects = Volunteer.objects.prospective_leaders_for_trip(trip)
        self.assertEqual(list(prospects), [])


class VolunteerManagerTestCase(ApplicationTestMixin, FytTestCase):
    def setUp(self):
        self.init_trips_year()
        self.q_general = mommy.make(
            Question, trips_year=self.trips_year, type=Question.ALL
        )
        self.q_leader = mommy.make(
            Question, trips_year=self.trips_year, type=Question.LEADER
        )
        self.q_croo = mommy.make(
            Question, trips_year=self.trips_year, type=Question.CROO
        )

        self.questions = [self.q_general, self.q_leader, self.q_croo]

        # Complete leader & croo app
        self.app1 = self.make_application()
        self.app1.answer_question(self.q_general, 'answer')
        self.app1.answer_question(self.q_leader, 'answer')
        self.app1.answer_question(self.q_croo, 'answer')

        # Complete leader
        self.app2 = self.make_application()
        self.app2.answer_question(self.q_general, 'answer')
        self.app2.answer_question(self.q_leader, 'answer')
        self.app2.answer_question(self.q_croo, '')

        # Complete croo
        self.app3 = self.make_application()
        self.app3.answer_question(self.q_general, 'answer')
        self.app3.answer_question(self.q_leader, '')
        self.app3.answer_question(self.q_croo, 'answer')

        # Not complete - missing croo & leader answer
        self.app4 = self.make_application()
        self.app4.answer_question(self.q_general, 'answer')

        # Not complete - empty answer
        self.app5 = self.make_application()
        self.app5.answer_question(self.q_general, '')
        self.app5.answer_question(self.q_leader, 'answer')
        self.app5.answer_question(self.q_croo, 'answer')

        # Not a leader app
        self.app6 = self.make_application()
        self.app6.answer_question(self.q_general, 'answer')
        self.app6.answer_question(self.q_leader, 'answer')
        self.app6.leader_willing = False
        self.app6.save()

        # Not a croo app
        self.app7 = self.make_application()
        self.app7.answer_question(self.q_general, 'answer')
        self.app7.answer_question(self.q_croo, 'answer')
        self.app7.croo_willing = False
        self.app7.save()

    def test_get_leader_applications(self):
        qs = Volunteer.objects.leader_applications(self.trips_year)
        self.assertQsEqual(qs, [self.app1, self.app2])

    def test_get_croo_applications(self):
        qs = Volunteer.objects.croo_applications(self.trips_year)
        self.assertQsEqual(qs, [self.app1, self.app3])

    def test_get_leader_or_croo_applications(self):
        with self.assertNumQueries(3):
            qs = Volunteer.objects.leader_or_croo_applications(self.trips_year)
            self.assertQsEqual(qs, [self.app1, self.app2, self.app3])

    def test_get_leader_and_croo_applications(self):
        with self.assertNumQueries(3):
            qs = Volunteer.objects.leader_and_croo_applications(self.trips_year)
            self.assertQsEqual(qs, [self.app1])

    def test_incomplete_leader_applications(self):
        qs = Volunteer.objects.incomplete_leader_applications(self.trips_year)
        self.assertQsEqual(qs, [self.app3, self.app4, self.app5, self.app7])

    def test_incomplete_croo_applications(self):
        qs = Volunteer.objects.incomplete_croo_applications(self.trips_year)
        self.assertQsEqual(qs, [self.app2, self.app4, self.app5, self.app6])

    def test_leaders(self):
        trips_year = self.init_trips_year()
        leader = make_application(
            trips_year=trips_year,
            status=Volunteer.LEADER,
            trip_assignment=mommy.make(Trip),
        )
        not_leader = make_application(trips_year=trips_year, trip_assignment=None)
        self.assertQsEqual(Volunteer.objects.leaders(trips_year), [leader])

    def test_croo_members(self):
        trips_year = self.init_trips_year()
        croo = make_application(trips_year=trips_year, status=Volunteer.CROO)
        not_croo = self.make_application(trips_year=trips_year)
        self.assertQsEqual(Volunteer.objects.croo_members(trips_year), [croo])

    def test_leader_waitist(self):
        trips_year = self.init_trips_year()
        waitlisted = make_application(
            trips_year=trips_year, status=Volunteer.LEADER_WAITLIST
        )
        self.assertQsEqual(Volunteer.objects.leader_waitlist(trips_year), [waitlisted])

    def test_rejected(self):
        rejected = self.make_application(status=Volunteer.REJECTED)
        other = self.make_application(status=Volunteer.PENDING)
        self.assertQsEqual(Volunteer.objects.rejected(self.trips_year), [rejected])

    def test_with_avg_scores_ordering(self):
        self.make_score_values()
        app1 = self.make_application()
        app2 = self.make_application()
        mommy.make(Grader).add_score(app1, self.V2, self.V1)

        qs = Volunteer.objects.with_avg_scores()
        qs = qs.order_by('-norm_avg_leader_score')

        self.assertEqual(qs[0].avg_leader_score, 2)
        self.assertEqual(qs[0].avg_croo_score, 1)
        self.assertEqual(qs[0].norm_avg_leader_score, 2)
        self.assertEqual(qs[0].norm_avg_croo_score, 1)

        self.assertEqual(qs[1].avg_leader_score, None)
        self.assertEqual(qs[1].avg_croo_score, None)
        self.assertEqual(qs[1].norm_avg_leader_score, 0)
        self.assertEqual(qs[1].norm_avg_croo_score, 0)

    def test_with_required_questions(self):
        self.assertQsEqual(self.app1.required_questions, self.questions)

        # Test preloading
        qs = Volunteer.objects.with_required_questions(self.trips_year)
        with self.assertNumQueries(0):
            for v in qs:
                self.assertQsEqual(v.required_questions, self.questions)


class ApplicationFormTestCase(FytTestCase):
    def setUp(self):
        self.trips_year = self.init_trips_year()
        self.app = make_application(trips_year=self.trips_year)
        self.question = mommy.make(
            Question,
            trips_year=self.trips_year,
            pk=1,
            index=0,
            question="Favorite fruit?",
            type='LEADER',
        )

    def test_question_fields(self):
        form = QuestionForm(instance=self.app, data={'question_1': 'Blueberries'})
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(
            form.fields['question_1'].label,
            'PLEASE ANSWER THIS IF YOU ARE APPLYING TO BE A TRIP LEADER. Favorite fruit?',
        )

        answers = self.app.answer_set.all()
        self.assertEqual(len(answers), 1)
        self.assertEqual(answers[0].question, self.question)
        self.assertEqual(answers[0].answer, 'Blueberries')

    def test_question_field_word_count(self):
        form = QuestionForm(instance=self.app, data={'question_1': 'word ' * 301})
        self.assertFalse(form.is_valid())


class AgreementFormTestCase(FytTestCase):
    def setUp(self):
        self.trips_year = self.init_trips_year()
        self.app = make_application(trips_year=self.trips_year)

    def test_agreement_form_validation(self):
        form = AgreementForm(instance=self.app, data={
            'trippee_confidentiality': True,
            'in_goodstanding_with_college': False,
            'trainings': True
        })
        self.assertFalse(form.is_valid())
        self.app.refresh_from_db()
        self.assertFalse(self.app.submitted)

    def test_agreement_form_submits_application(self):
        form = AgreementForm(instance=self.app, data={
            'trippee_confidentiality': True,
            'in_goodstanding_with_college': True,
            'trainings': True
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.app.refresh_from_db()
        self.assertTrue(self.app.submitted)
        # TODO: test all conditions are set


class LeaderSupplementFormTestCase(FytTestCase):
    def setUp(self):
        self.trips_year = self.init_trips_year()
        self.section = mommy.make(
            Section,
            trips_year=self.trips_year,
            pk=1,
            name='A',
            leaders_arrive=date(2015, 1, 1),
        )
        self.app = make_application(trips_year=self.trips_year)
        self.leader_app = self.app.leader_supplement

    def data(self, additional):
        d = {
            'class_2_3_paddler': True,
            'ledyard_level_2': True,
            'ledyard_level_1': True,
            'climbing_course': True,
            'dmc_leader': True,
            'cnt_leader': True,
            'dmbc_leader': True,
        }
        d.update(additional)
        return d

    def test_adds_section_fields(self):
        form = LeaderSupplementForm(trips_year=self.trips_year)
        self.assertIn('section_1', form.fields)

    def test_section_field_label(self):
        form = LeaderSupplementForm(trips_year=self.trips_year)
        self.assertEqual(form.fields['section_1'].label, 'A &mdash; Jan 01 to Jan 06')

    def test_default_section_choice(self):
        form = LeaderSupplementForm(instance=self.leader_app, data=self.data({}))
        self.assertEqual(form.fields['section_1'].initial, 'NOT AVAILABLE')

    def test_initial_section_choice_is_populated(self):
        self.leader_app.set_section_preference(self.section, 'PREFER')
        form = LeaderSupplementForm(instance=self.leader_app)
        self.assertEqual(form.fields['section_1'].initial, 'PREFER')

    def test_new_section_choice_is_saved(self):
        form = LeaderSupplementForm(
            instance=self.leader_app, data=self.data({'section_1': 'AVAILABLE'})
        )
        form.save()

        prefs = self.leader_app.leadersectionchoice_set.all()
        self.assertEqual(len(prefs), 1)
        self.assertEqual(prefs[0].section, self.section)
        self.assertEqual(prefs[0].preference, 'AVAILABLE')

    def test_existing_section_choice_is_updated(self):
        # Initial choice
        self.leader_app.set_section_preference(self.section, 'PREFER')

        form = LeaderSupplementForm(
            instance=self.leader_app, data=self.data({'section_1': 'AVAILABLE'})
        )
        form.save()

        prefs = self.leader_app.leadersectionchoice_set.all()
        self.assertEqual(len(prefs), 1)
        self.assertEqual(prefs[0].section, self.section)
        self.assertEqual(prefs[0].preference, 'AVAILABLE')

    def test_formfield_names(self):
        mommy.make(Section, trips_year=self.trips_year, pk=3, name='C')
        form = LeaderSupplementForm(trips_year=self.trips_year)

        self.assertEqual(
            form.section_handler.formfield_names(), ['section_1', 'section_3']
        )

    def test_triptype_field(self):
        triptype1 = mommy.make(
            TripType, name='Climbing', trips_year=self.trips_year, pk=1
        )

        form = LeaderSupplementForm(
            instance=self.leader_app,
            data=self.data({'triptype_1': 'NOT AVAILABLE', 'section_1': 'PREFER'}),
        )
        form.save()

        self.assertEqual(form.fields['triptype_1'].label, 'Climbing')

        prefs = self.leader_app.leadertriptypechoice_set.all()
        self.assertEqual(len(prefs), 1)
        self.assertEqual(prefs[0].triptype, triptype1)
        self.assertEqual(prefs[0].preference, 'NOT AVAILABLE')


class DbVolunteerViewsTestCase(ApplicationTestMixin, FytTestCase):
    def setUp(self):
        self.init_trips_year()
        self.init_old_trips_year()

    def test_directorate_can_normally_see_volunteer_pages(self):
        mommy.make(Timetable, hide_volunteer_page=False)
        url = reverse('core:volunteer:index', kwargs={'trips_year': self.trips_year})
        res = self.app.get(url, user=self.make_director())
        res = self.app.get(url, user=self.make_grader(), status=403)
        res = self.app.get(url, user=self.make_directorate())
        res = self.app.get(url, user=self.make_tlt())

    def test_hiding_volunteer_page_restricts_access_to_directors_only(self):
        mommy.make(Timetable, hide_volunteer_page=True)
        url = reverse('core:volunteer:index', kwargs={'trips_year': self.trips_year})
        res = self.app.get(url, user=self.make_director())
        res = self.app.get(url, user=self.make_grader(), status=403)
        res = self.app.get(url, user=self.make_directorate(), status=403)
        res = self.app.get(url, user=self.make_tlt())

    def test_volunteer_index_only_shows_complete_applications(self):
        mommy.make(Timetable)
        complete = self.make_application()
        incomplete = self.make_application(croo_willing=False, leader_willing=False)

        url = reverse('core:landing_page', kwargs={'trips_year': self.trips_year})
        res = self.app.get(url, user=self.make_director())
        url = reverse('core:volunteer:index', kwargs={'trips_year': self.trips_year})
        res = res.click(href=url)

        self.assertContains(res, str(complete))
        self.assertNotContains(res, str(incomplete))

    def test_old_applications_are_hidden(self):
        mommy.make(Timetable)
        mommy.make(ApplicationInformation, trips_year=self.old_trips_year)
        mommy.make(ApplicationInformation, trips_year=self.trips_year)

        tlt = self.make_tlt()
        director = self.make_director()

        old_app = self.make_application(trips_year=self.old_trips_year)
        new_app = self.make_application(trips_year=self.trips_year)

        # year, user, should they be able to see the page?
        cases = [
            (old_app, tlt, 403),
            (old_app, director, 200),
            (new_app, tlt, 200),
            (new_app, director, 200),
        ]

        for application, user, status in cases:
            urls = [
                application.index_url(),
                application.detail_url(),
                application.update_url(),
                reverse(
                    'core:volunteer:update_status', kwargs=application.obj_kwargs()
                ),
                reverse('core:volunteer:update_admin', kwargs=application.obj_kwargs()),
            ]

            for url in urls:
                self.app.get(url, user=user, status=status)

    def test_remove_leader_assignment(self):
        mommy.make(Timetable)
        self.make_director()
        application = self.make_application(
            status=Volunteer.LEADER,
            trip_assignment=mommy.make(Trip, trips_year=self.trips_year),
        )

        resp1 = self.app.get(application.detail_url(), user=self.director)
        resp2 = resp1.click(description='remove')
        resp3 = resp2.form.submit().follow()

        application.refresh_from_db()
        self.assertIsNone(application.trip_assignment)


class PortalContentModelTestCase(ApplicationTestMixin, FytTestCase):
    def test_get_status_description(self):
        trips_year = self.init_trips_year()
        content = mommy.make(
            PortalContent,
            trips_year=trips_year,
            PENDING_description='pending',
            CROO_description='croo',
            LEADER_description='leader',
            LEADER_WAITLIST_description='waitlist',
            REJECTED_description='rejected',
            CANCELED_description='cancelled',
        )
        for choice, label in Volunteer.STATUS_CHOICES:
            self.assertEqual(
                getattr(content, "%s_description" % choice),
                content.get_status_description(choice),
            )


class ApplicationViewsTestCase(ApplicationTestMixin, FytTestCase):
    def setUp(self):
        self.init_trips_year()
        mommy.make(ApplicationInformation, trips_year=self.trips_year)

    def test_deadline_extension(self):
        application = self.make_application()

        # OK: Regular application, within regular application period
        self.open_application()
        url = reverse('applications:apply')
        resp = self.app.get(url, user=application.applicant).maybe_follow()
        self.assertTemplateUsed(resp, 'applications/application.html')

        # NO: deadline passed, not available
        self.close_application()
        resp = self.app.get(url, user=application.applicant).maybe_follow()
        self.assertTemplateUsed(resp, 'applications/not_available.html')

        # NO: no existing application
        resp = self.app.get(url, user=mommy.make(DartmouthUser)).maybe_follow()
        self.assertTemplateUsed(resp, 'applications/not_available.html')

        # OK: application extension
        application.deadline_extension = timezone.now() + timedelta(1)
        application.save()
        resp = self.app.get(url, user=application.applicant).maybe_follow()
        self.assertTemplateUsed(resp, 'applications/application.html')


class ApplicationAdminFormTestCase(ApplicationTestMixin, FytTestCase):
    def setUp(self):
        self.init_trips_year()
        self.init_old_trips_year()
        self.application = self.make_application()

    def test_trip_queryset_is_only_for_current_year(self):
        form = ApplicationAdminForm(instance=self.application)
        t1 = mommy.make(Trip, trips_year=self.trips_year)
        t2 = mommy.make(Trip, trips_year=self.old_trips_year)
        self.assertQsEqual(form.fields['trip_assignment'].queryset, [t1])

    def test_croo_queryset_is_only_for_current_year(self):
        form = ApplicationAdminForm(instance=self.application)
        c1 = mommy.make(Croo, trips_year=self.trips_year)
        c2 = mommy.make(Croo, trips_year=self.old_trips_year)
        self.assertQsEqual(form.fields['croo_assignment'].queryset, [c1])
