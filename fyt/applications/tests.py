
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from model_mommy import mommy

from .forms import CrooApplicationGradeForm
from .models import (
    Answer,
    ApplicationInformation,
    CrooApplicationGrade,
    CrooSupplement,
    GeneralApplication,
    LeaderApplicationGrade,
    LeaderSupplement as LeaderApplication,
    PortalContent,
    QualificationTag,
    SkippedCrooGrade,
    SkippedLeaderGrade,
    Question,
)

from fyt.applications.views.graders import get_graders
from fyt.applications.views.grading import SHOW_GRADE_AVG_INTERVAL, SKIP
from fyt.croos.models import Croo
from fyt.test.testcases import TripsYearTestCase as TripsTestCase, WebTestCase
from fyt.timetable.models import Timetable
from fyt.trips.models import Section, Trip, TripType
from fyt.utils.choices import AVAILABLE, PREFER


def make_application(status=GeneralApplication.PENDING, trips_year=None,
                     assigned_trip=None):

    application = mommy.make(
        GeneralApplication,
        status=status,
        trips_year=trips_year,
        assigned_trip=assigned_trip,
        document='some/file',
        leader_willing=True,
        croo_willing=True)

    leader_app = mommy.make(
        LeaderApplication,
        application=application,
        trips_year=trips_year)

    croo_app = mommy.make(
        CrooSupplement,
        application=application,
        trips_year=trips_year)

    return application


class ApplicationTestMixin():

    """ Common utilities for testing applications """

    def open_application(self):
        """" open leader applications """
        t = Timetable.objects.timetable()
        t.applications_open += timedelta(-1)
        t.applications_close += timedelta(1)
        t.save()

    def close_application(self):
        """ close leader applications """
        t = Timetable.objects.timetable()
        t.applications_open += timedelta(-2)
        t.applications_close += timedelta(-1)
        t.save()

    def make_application(self, trips_year=None, **kwargs):
        if trips_year is None:
            trips_year = self.current_trips_year
        return make_application(trips_year=trips_year, **kwargs)


class ApplicationModelTestCase(ApplicationTestMixin, TripsTestCase):

    def test_must_be_LEADER_to_be_assigned_trip(self):
        trips_year = self.init_current_trips_year()
        for status in ['PENDING', 'LEADER_WAITLIST', 'CROO', 'REJECTED', 'CANCELED']:
            application = mommy.make(
                    GeneralApplication,
                    status=getattr(GeneralApplication, status),
                    trips_year=trips_year,
                    trippee_confidentiality=True,
                    in_goodstanding_with_college=True,
                    trainings=True
            )
            application.assigned_trip = mommy.make(Trip, trips_year=trips_year)
            with self.assertRaises(ValidationError):
                    application.full_clean()

        application.status = GeneralApplication.LEADER
        application.full_clean()

    def test_must_be_CROO_to_be_assigned_croo(self):
        trips_year = self.init_current_trips_year()
        for status in ['PENDING', 'LEADER_WAITLIST', 'LEADER', 'REJECTED', 'CANCELED']:
            application = mommy.make(
                GeneralApplication,
                status=getattr(GeneralApplication, status),
                trips_year=trips_year,
                trippee_confidentiality=True,
                in_goodstanding_with_college=True,
                trainings=True
            )
            application.assigned_croo = mommy.make(Croo, trips_year=trips_year)
            with self.assertRaises(ValidationError):
                    application.full_clean()

        application.status = GeneralApplication.CROO
        application.full_clean()

    def test_get_preferred_trips(self):
        trips_year = self.init_current_trips_year()
        application = self.make_application(trips_year=trips_year)
        ls = application.leader_supplement
        preferred_trip = mommy.make(Trip, trips_year=trips_year)
        ls.set_section_preference(preferred_trip.section, PREFER)
        ls.set_triptype_preference(preferred_trip.template.triptype, PREFER)
        not_preferred_trip = mommy.make(Trip, trips_year=trips_year)
        self.assertEqual([preferred_trip], list(application.get_preferred_trips()))

    def test_get_available_trips(self):
        trips_year = self.init_current_trips_year()
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

        make = lambda s,t: mommy.make(Trip, trips_year=trips_year, section=s, template__triptype=t)
        preferred_trip = make(preferred_section, preferred_triptype)
        available_trips = [  # all other permutations
            make(preferred_section, available_triptype),
            make(available_section, preferred_triptype),
            make(available_section, available_triptype),
        ]
        not_preferred_trip = mommy.make(Trip, trips_year=trips_year)
        self.assertEqual(set(available_trips), set(application.get_available_trips()))

    def test_get_first_aid_cert(self):
        trips_year = self.init_current_trips_year()
        application = mommy.make(GeneralApplication, trips_year=trips_year,
                                 fa_cert='WFR')
        self.assertEqual(application.get_first_aid_cert(), 'WFR')

    def test_get_first_aid_cert_other(self):
        application = mommy.make(
            GeneralApplication,
            fa_cert=GeneralApplication.OTHER,
            fa_other='ABC'
        )
        self.assertEqual(application.get_first_aid_cert(), 'ABC')

    def test_get_first_aid_cert_without_explicit_other(self):
        application = mommy.make(
            GeneralApplication,
            fa_cert="",
            fa_other='ABC'
        )
        self.assertEqual(application.get_first_aid_cert(), 'ABC')

    def test_must_agree_to_trippee_confidentiality(self):
        with self.assertRaisesMessage(ValidationError, 'condition'):
            mommy.make(GeneralApplication,
                       trippee_confidentiality=False,
                       in_goodstanding_with_college=True,
                       trainings=True
            ).full_clean()

    def test_must_be_in_good_standing(self):
        with self.assertRaisesRegex(ValidationError, 'condition'):
            mommy.make(GeneralApplication,
                       trippee_confidentiality=True,
                       in_goodstanding_with_college=False,
                       trainings=True
            ).full_clean()

    def test_must_agree_to_trainings(self):
        with self.assertRaisesRegex(ValidationError, 'condition'):
            mommy.make(GeneralApplication,
                       trippee_confidentiality=True,
                       in_goodstanding_with_college=True,
                       trainings=False
            ).full_clean()

    def test_set_section_preference(self):
        trips_year=self.init_trips_year()
        ls = self.make_application(trips_year=trips_year).leader_supplement
        section = mommy.make(Section, trips_year=trips_year)
        ls.set_section_preference(section, PREFER)

        self.assertEqual(len(ls.leadersectionchoice_set.all()), 1)
        pref = ls.leadersectionchoice_set.first()
        self.assertEqual(pref.section, section)
        self.assertEqual(pref.preference, PREFER)

    def test_set_triptype_preference(self):
        trips_year=self.init_trips_year()
        ls = self.make_application(trips_year=trips_year).leader_supplement
        triptype = mommy.make(TripType, trips_year=trips_year)
        ls.set_triptype_preference(triptype, AVAILABLE)

        self.assertEqual(len(ls.leadertriptypechoice_set.all()), 1)
        pref = ls.leadertriptypechoice_set.first()
        self.assertEqual(pref.triptype, triptype)
        self.assertEqual(pref.preference, AVAILABLE)

    def test_leader_application_complete(self):
        trips_year = self.init_trips_year()
        app = make_application(trips_year=trips_year)

        app.leader_willing = False
        self.assertFalse(app.leader_application_complete)

        app.leader_willing = True
        self.assertTrue(app.leader_application_complete)

        # Not complete because there is an unanswered question
        question = mommy.make(Question, trips_year=trips_year)
        self.assertFalse(app.leader_application_complete)

        # Not complete because there is a blank answer
        answer = mommy.make(Answer, application=app, question=question, answer="")
        self.assertFalse(app.leader_application_complete)

        # Complete - answered
        answer.answer = 'Some text!'
        answer.save()
        self.assertTrue(app.leader_application_complete)

    def test_croo_application_complete(self):
        trips_year = self.init_trips_year()
        app = make_application(trips_year=trips_year)

        app.croo_willing = False
        self.assertFalse(app.croo_application_complete)

        app.croo_willing = True
        self.assertTrue(app.croo_application_complete)

        # Not complete because there is an unanswered question
        question = mommy.make(Question, trips_year=trips_year)
        self.assertFalse(app.croo_application_complete)

        # Not complete because there is a blank answer
        answer = mommy.make(Answer, application=app, question=question, answer="")
        self.assertFalse(app.croo_application_complete)

        # Complete - answered
        answer.answer = 'Some text!'
        answer.save()
        self.assertTrue(app.croo_application_complete)

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


class ApplicationAccessTestCase(ApplicationTestMixin, WebTestCase):

    def test_anonymous_user_does_not_crash_application(self):
        self.init_current_trips_year()
        self.app.get(reverse('applications:apply'))

    def test_application_not_visible_if_not_available(self):
        self.init_current_trips_year()
        self.close_application()
        self.mock_user()
        response = self.app.get(reverse('applications:apply'), user=self.user)
        self.assertTemplateUsed(response, 'applications/not_available.html')


class ApplicationFormTestCase(ApplicationTestMixin, WebTestCase):

    csrf_checks = False

    def setUp(self):
        self.init_current_trips_year()
        self.init_previous_trips_year()

    def test_file_uploads_dont_overwrite_each_other(self):
            # TODO / scrap
        self.mock_user()
        self.open_application()

        res = self.app.get(reverse('applications:apply'), user=self.user)
        # print(res)
        #  print(res.form)


class ApplicationManagerTestCase(ApplicationTestMixin, TripsTestCase):
    """
    Tested against the LeaderApplication model only;
    there should be no difference with the CrooApplciation model.
    """
    def setUp(self):
            self.init_current_trips_year()
            self.init_previous_trips_year()
            self.mock_user()

    def test_dont_grade_incomplete_application(self):
        app1 = self.make_application()
        app1.document = ''
        app1.save()

        app2 = self.make_application()
        app2.leader_willing = False
        app2.save()

        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next)

    def test_with_no_grades(self):
        application = self.make_application()

        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertEqual(application.leader_supplement, next)

    def test_graded_ungraded_priority(self):
        app1 = self.make_application()
        grade = mommy.make(LeaderApplicationGrade, trips_year=self.current_trips_year,
                           application=app1.leader_supplement)
        app2 = self.make_application()

        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertEqual(next, app2.leader_supplement, 'app with no grades should have priority')

    def test_user_can_only_grade_application_once(self):
        application = self.make_application()
        grade = mommy.make(LeaderApplicationGrade, grader=self.user,
                           application=application.leader_supplement,
                           trips_year=self.trips_year)

        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'no applications should be available')

    def test_only_grade_pending_applications(self):
        self.make_application(status=GeneralApplication.LEADER)
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'only PENDING apps should be gradable')

    def test_can_only_grade_applications_for_the_current_trips_year(self):
        self.make_application(trips_year=self.previous_trips_year)
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'should not be able to grade apps from previous years')

    def test_correct_number_of_grades(self):
        application = self.make_application()
        for i in range(LeaderApplication.NUMBER_OF_GRADES):
                mommy.make(
                    LeaderApplicationGrade,
                    trips_year=self.trips_year,
                    application=application.leader_supplement
                )
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'can only grade NUMBER_OF_GRADES times')

    def test_skipped_applications_are_not_returned(self):
        application = self.make_application()
        grader = self.mock_grader()
        skip = mommy.make(SkippedLeaderGrade, application=application.leader_supplement,
                          trips_year=self.trips_year, grader=grader)

        next = LeaderApplication.objects.next_to_grade(grader)
        self.assertIsNone(next)


class ApplicationManager_prospective_leaders_TestCase(ApplicationTestMixin, TripsTestCase):

    def setUp(self):
        self.init_current_trips_year()

    def test_prospective_leader_with_preferred_choices(self):
        trip = mommy.make(Trip, trips_year=self.current_trips_year)

        app = self.make_application(status=GeneralApplication.LEADER)
        app.leader_supplement.set_section_preference(trip.section, PREFER)
        app.leader_supplement.set_triptype_preference(trip.template.triptype, PREFER)

        prospects = GeneralApplication.objects.prospective_leaders_for_trip(trip)
        self.assertEquals(list(prospects), [app])

    def test_prospective_leader_with_available_choices(self):
        trip = mommy.make(Trip, trips_year=self.current_trips_year)

        app = self.make_application(status=GeneralApplication.LEADER_WAITLIST)
        app.leader_supplement.set_section_preference(trip.section, AVAILABLE)
        app.leader_supplement.set_triptype_preference(trip.template.triptype, AVAILABLE)

        prospects = GeneralApplication.objects.prospective_leaders_for_trip(trip)
        self.assertEquals(list(prospects), [app])

    def test_only_complete_applications(self):
        trip = mommy.make(Trip, trips_year=self.current_trips_year)
        prospective = self.make_application(status=GeneralApplication.LEADER_WAITLIST)
        prospective.leader_supplement.set_section_preference(trip.section, AVAILABLE)
        prospective.leader_supplement.set_triptype_preference(trip.template.triptype, AVAILABLE)

        not_prosp = self.make_application(status=GeneralApplication.LEADER_WAITLIST)
        not_prosp.leader_supplement.set_section_preference(trip.section, AVAILABLE)
        not_prosp.leader_supplement.set_triptype_preference(trip.template.triptype, AVAILABLE)
        not_prosp.document = ''
        not_prosp.save()

        prospects = GeneralApplication.objects.prospective_leaders_for_trip(trip)
        self.assertEquals(list(prospects), [prospective])

    def test_without_section_preference(self):
        trip = mommy.make(Trip, trips_year=self.current_trips_year)

        # otherwise available
        app = self.make_application(status=GeneralApplication.LEADER)
        app.leader_supplement.set_triptype_preference(trip.template.triptype, PREFER)

        prospects = GeneralApplication.objects.prospective_leaders_for_trip(trip)
        self.assertEquals(list(prospects), [])

    def test_without_triptype_preference(self):
        trip = mommy.make(Trip, trips_year=self.current_trips_year)

        app = self.make_application(status=GeneralApplication.LEADER)
        app.leader_supplement.set_section_preference(trip.section, PREFER)

        prospects = GeneralApplication.objects.prospective_leaders_for_trip(trip)
        self.assertEquals(list(prospects), [])


class GeneralApplicationManagerTestCase(ApplicationTestMixin, TripsTestCase):

    def test_get_leader_applications(self):
        trips_year = self.init_current_trips_year()
        question = mommy.make(Question, trips_year=trips_year)

        # Complete
        app1 = self.make_application(trips_year=trips_year)
        app1.answer_question(question, 'An answer!')

        # Not complete - empty answer
        app2 = self.make_application(trips_year=trips_year)
        app2.answer_question(question, "")

        # Not complete - missing answer
        app3 = self.make_application(trips_year=trips_year)

        # Not a leader application
        app4 = self.make_application(trips_year=trips_year)
        app4.leader_willing = False
        app4.save()

        # Complete
        qs = GeneralApplication.objects.leader_applications(trips_year)
        self.assertQsEqual(qs, [app1])

        # Incomplete
        qs = GeneralApplication.objects.incomplete_leader_applications(trips_year)
        self.assertQsEqual(qs, [app2, app3, app4])

    def test_get_croo_applications(self):
        trips_year = self.init_current_trips_year()
        question = mommy.make(Question, trips_year=trips_year)

        # Complete
        app1 = self.make_application(trips_year=trips_year)
        app1.answer_question(question, 'An answer!')

        # Not complete - empty answer
        app2 = self.make_application(trips_year=trips_year)
        app2.answer_question(question, "")

        # Not complete - missing answer
        app3 = self.make_application(trips_year=trips_year)

        # Not a croo application
        app4 = self.make_application(trips_year=trips_year)
        app4.croo_willing = False
        app4.save()

        # Complete
        qs = GeneralApplication.objects.croo_applications(trips_year)
        self.assertQsEqual(qs, [app1])

        # Incomplete
        qs = GeneralApplication.objects.incomplete_croo_applications(trips_year)
        self.assertQsEqual(qs, [app2, app3, app4])

    def test_get_leader_or_croo_applications(self):
        trips_year = self.init_current_trips_year()
        question = mommy.make(Question, trips_year=trips_year)

        app1 = self.make_application(trips_year=trips_year)
        app1.answer_question(question, 'An answer!')
        app1.leader_willing = False
        app1.save()

        app2 = self.make_application(trips_year=trips_year)
        app2.answer_question(question, 'An answer!')
        app2.croo_willing = False
        app2.save()

        app3 = self.make_application(trips_year=trips_year)
        app3.answer_question(question, 'An answer!')
        app3.leader_willing = False
        app3.croo_willing = False
        app3.save()

        app4 = self.make_application(trips_year=trips_year)

        app5 = self.make_application(trips_year=trips_year)
        app5.answer_question(question, '')

        qs = GeneralApplication.objects.leader_or_croo_applications(trips_year)
        self.assertEqual(set(qs), set([app1, app2]))

    def test_leaders(self):
        trips_year = self.init_trips_year()
        leader = make_application(
                trips_year=trips_year,
                status=GeneralApplication.LEADER,
                assigned_trip=mommy.make(Trip)
        )
        not_leader = make_application(
                trips_year=trips_year,
                assigned_trip=None
        )
        self.assertQsEqual(GeneralApplication.objects.leaders(trips_year), [leader])

    def test_croo_members(self):
        trips_year = self.init_trips_year()
        croo = make_application(
                trips_year=trips_year,
                status=GeneralApplication.CROO
        )
        not_croo = self.make_application(trips_year=trips_year)
        self.assertQsEqual(GeneralApplication.objects.croo_members(trips_year), [croo])


class GradeViewsTestCase(ApplicationTestMixin, WebTestCase):

    def setUp(self):
        self.init_current_trips_year()
        self.mock_director()
        self.mock_user()

    grade_views = ['applications:grade:next_leader',
                   #'applications:grade:leader',
                   'applications:grade:no_leaders_left',
                   'applications:grade:next_croo',
                   #'applications:grade:croo',
                   'applications:grade:no_croo_left']

    def test_not_gradeable_before_application_deadline(self):
        self.open_application()
        for view in self.grade_views:
                res = self.app.get(reverse(view), user=self.director).maybe_follow()
                self.assertTemplateUsed(res, 'applications/grading_not_available.html')

    def test_gradable_after_application_deadline(self):
        self.close_application() # puts deadline in the past
        for view in self.grade_views:
                res = self.app.get(reverse(view), user=self.director).maybe_follow()
                self.assertTemplateNotUsed(res, 'applications/grading_not_available.html')


class GradingViewTestCase(ApplicationTestMixin, WebTestCase):

    def test_show_average_grade_every_interval_in_messages(self):
        trips_year = self.init_current_trips_year()
        grader = self.mock_grader()
        self.close_application()

        application = self.make_application(trips_year=trips_year).leader_supplement

        for i in range(SHOW_GRADE_AVG_INTERVAL):
                mommy.make(LeaderApplicationGrade, trips_year=trips_year, grader=grader)

        res = self.app.get(reverse('applications:grade:next_leader'), user=grader).follow()
        messages = list(res.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('average', messages[0].message)

    def test_redirect_to_next_for_qualification_does_not_break(self):
        self.init_current_trips_year()
        self.mock_director()

        self.close_application() # open grading

        # setup application with one grade suggesting a Croo
        app = self.make_application()
        qualification = mommy.make(QualificationTag, trips_year=self.trips_year)
        grade = mommy.make(CrooApplicationGrade, application=app.croo_supplement,
                           qualifications=[qualification], trips_year=self.trips_year)

        # try and grade only for that croo
        res = self.app.get(reverse('applications:grade:next_croo',
                                   kwargs={'qualification_pk': qualification.pk}),
                           user=self.director)

    def test_skips_applications_adds_skip_object_to_database(self):
        trips_year = self.init_current_trips_year()
        application = self.make_application(trips_year=trips_year)
        grader = self.mock_grader()

        res = self.app.get(reverse('applications:grade:leader',
                                   kwargs={'pk': application.leader_supplement.pk}), user=grader)
        res2 = res.form.submit(SKIP)

        skips = SkippedLeaderGrade.objects.all()
        self.assertEqual(len(skips), 1)
        skip = skips[0]
        self.assertEqual(skip.grader, grader)
        self.assertEqual(skip.application, application.leader_supplement)

        # and we shouldn't see the application anymore
        res = self.app.get(reverse('applications:grade:next_leader'),
                           user=grader).follow()
        self.assertTemplateUsed(res, 'applications/no_applications.html')

    def test_skipped_app_in_normal_view_is_shown_again_in_qualification_specific_view(self):
        trips_year = self.init_current_trips_year()
        self.close_application()
        application = self.make_application(trips_year=trips_year)
        # directors have permission to grade croo apps
        grader = self.mock_director()

        # skip an application in normal grading
        res = self.app.get(reverse('applications:grade:croo',
                                   kwargs={'pk': application.croo_supplement.pk}), user=grader)
        res2 = res.form.submit(SKIP)

        # make a qualification and stick the tag on this qualification
        qualification = mommy.make(QualificationTag, trips_year=trips_year)
        grade = mommy.make(CrooApplicationGrade, application=application.croo_supplement,
                           qualifications=[qualification], trips_year=trips_year)

        res = self.app.get(reverse('applications:grade:next_croo',
                                   kwargs={'qualification_pk': qualification.pk}),
                           user=grader).follow()
        self.assertEqual(res.context['view'].get_application(), application.croo_supplement)

    def test_skiping_application_in_qualification_grading_adds_skip_object_to_database(self):
        trips_year = self.init_current_trips_year()
        application = self.make_application(trips_year=trips_year)
        grader = self.mock_director()

        # make a qualification and tag this application
        qualification = mommy.make(QualificationTag, trips_year=trips_year)
        grade = mommy.make(CrooApplicationGrade, application=application.croo_supplement,
                           qualifications=[qualification], trips_year=trips_year)

        res = self.app.get(reverse('applications:grade:next_croo',
                                   kwargs={'qualification_pk': qualification.pk}),
                           user=grader).follow()
        res = res.form.submit(SKIP)

        # skip now exists,
        skips = SkippedCrooGrade.objects.all()
        self.assertEqual(len(skips), 1)
        skip = skips[0]
        self.assertEqual(skip.grader, grader)
        self.assertEqual(skip.application, application.croo_supplement)
        # and was added for this qualification:
        self.assertEqual(skip.for_qualification, qualification)

        # and we shouldn't see the application anymore
        res = self.app.get(reverse('applications:grade:next_croo'),
                           user=grader).follow()
        self.assertTemplateUsed(res, 'applications/no_applications.html')

    def test_skipped_app_for_qualification_is_not_shown_again_in_qualification_grading(self):
        trips_year = self.init_current_trips_year()
        self.close_application()
        application = self.make_application(trips_year=trips_year)
        # directors have permission to grade croo apps
        grader = self.mock_director()

        # make a qualification
        qualification = mommy.make(QualificationTag, trips_year=trips_year)

        # and stick the qualification on this application
        grade = mommy.make(CrooApplicationGrade, application=application.croo_supplement,
                           qualifications=[qualification], trips_year=trips_year)

        res = self.app.get(reverse('applications:grade:next_croo',
                                   kwargs={'qualification_pk': qualification.pk}),
                           user=grader).follow()
        res.form.submit(SKIP)

        res = self.app.get(reverse('applications:grade:next_croo',
                                   kwargs={'qualification_pk': qualification.pk}),
                           user=grader).follow()
        self.assertTemplateUsed(res, 'applications/no_applications.html')

    def test_croo_qualifications_are_filtered_for_current_trips_year(self):
        trips_year = self.init_trips_year()
        qualification = mommy.make(
                QualificationTag,
                trips_year=self.init_old_trips_year()
        )
        form = CrooApplicationGradeForm()
        self.assertNotIn(qualification, form.fields['qualifications'].queryset)


class GradersDatabaseListViewTestCase(TripsTestCase):

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


class DeleteGradeViews(ApplicationTestMixin, WebTestCase):

    def test_delete_leader_grade_is_restricted_to_directors(self):
        trips_year = self.init_current_trips_year()
        grade = mommy.make(LeaderApplicationGrade, trips_year=trips_year)
        url = reverse('db:leaderapplicationgrade:delete', kwargs={'trips_year': trips_year, 'pk': grade.pk})
        res = self.app.get(url, user=self.mock_tlt(), status=403)
        res = self.app.get(url, user=self.mock_directorate(), status=403)
        res = self.app.get(url, user=self.mock_grader(), status=403)
        res = self.app.get(url, user=self.mock_director())

    def test_delete_croo_grade_is_restricted_to_directors(self):
        trips_year = self.init_current_trips_year()
        grade = mommy.make(CrooApplicationGrade, trips_year=trips_year)
        url = reverse('db:crooapplicationgrade:delete', kwargs={'trips_year': trips_year, 'pk': grade.pk})
        res = self.app.get(url, user=self.mock_tlt(), status=403)
        res = self.app.get(url, user=self.mock_directorate(), status=403)
        res = self.app.get(url, user=self.mock_grader(), status=403)
        res = self.app.get(url, user=self.mock_director())

    def test_delete_leader_grade_redirects_to_app(self):
        trips_year = self.init_current_trips_year()
        application = self.make_application(trips_year)
        grade = mommy.make(LeaderApplicationGrade, trips_year=trips_year, application=application.leader_supplement)
        url = reverse('db:leaderapplicationgrade:delete', kwargs={'trips_year': trips_year, 'pk': grade.pk})
        res = self.app.get(url, user=self.mock_director())
        res = res.form.submit()
        self.assertRedirects(res, application.detail_url())

    def test_delete_croo_grade_redirects_to_app(self):
        trips_year = self.init_current_trips_year()
        application = self.make_application(trips_year)
        grade = mommy.make(CrooApplicationGrade, trips_year=trips_year, application=application.croo_supplement)
        url = reverse('db:crooapplicationgrade:delete', kwargs={'trips_year': trips_year, 'pk': grade.pk})
        res = self.app.get(url, user=self.mock_director())
        res = res.form.submit()
        self.assertRedirects(res, application.detail_url())


class AssignLeaderToTripViewsTestCase(ApplicationTestMixin, WebTestCase):

    def test_assignment_view(self):
        trips_year = self.init_current_trips_year()
        application = self.make_application(
            trips_year=trips_year, status=GeneralApplication.LEADER
        )
        url = reverse('db:generalapplication:update_trip',
                      kwargs={'trips_year': trips_year, 'pk': application.pk})
        res = self.app.get(url, user=self.mock_director())


class AssignToCrooTestCase(ApplicationTestMixin, WebTestCase):

    def test_assignment_view(self):
        trips_year = self.init_current_trips_year()
        application = self.make_application(
            trips_year=trips_year, status=GeneralApplication.CROO
        )
        croo = mommy.make(Croo, trips_year=trips_year)
        url = reverse(
            'db:generalapplication:update_croo',
            kwargs={'trips_year': trips_year, 'pk': application.pk}
        )
        form = self.app.get(url, user=self.mock_director()).form
        form['assigned_croo'] = croo.pk
        res = form.submit()
        croo = Croo.objects.get(pk=croo.pk)
        self.assertEqual(list(croo.croo_members.all()), [application])


class DbVolunteerPagesAccessTestCase(WebTestCase):

    def test_directorate_can_normally_see_volunteer_pages(self):
        trips_year = self.init_current_trips_year()
        mommy.make(Timetable, hide_volunteer_page=False)
        url = reverse('db:generalapplication:index', kwargs={'trips_year': trips_year})
        res = self.app.get(url, user=self.mock_director())
        res = self.app.get(url, user=self.mock_grader(), status=403)
        res = self.app.get(url, user=self.mock_directorate())
        res = self.app.get(url, user=self.mock_tlt())

    def test_hiding_volunteer_page_restricts_access_to_directors_only(self):
        trips_year = self.init_current_trips_year()
        mommy.make(Timetable, hide_volunteer_page=True)
        url = reverse('db:generalapplication:index', kwargs={'trips_year': trips_year})
        res = self.app.get(url, user=self.mock_director())
        res = self.app.get(url, user=self.mock_grader(), status=403)
        res = self.app.get(url, user=self.mock_directorate(), status=403)
        res = self.app.get(url, user=self.mock_tlt())


class PortalContentModelTestCase(ApplicationTestMixin, TripsTestCase):

    def test_get_status_description(self):
        trips_year = self.init_current_trips_year()
        content = mommy.make(
            PortalContent, trips_year=trips_year,
            PENDING_description='pending',
            CROO_description='croo',
            LEADER_description='leader',
            LEADER_WAITLIST_description='waitlist',
            REJECTED_description='rejected',
            CANCELED_description='cancelled'
        )
        for choice, label in GeneralApplication.STATUS_CHOICES:
            self.assertEqual(
                getattr(content, "%s_description" % choice),
                content.get_status_description(choice)
            )
