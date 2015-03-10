
from datetime import datetime
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from model_mommy import mommy

from doc.test.fixtures import TripsYearTestCase as TripsTestCase, WebTestCase
from doc.applications.models import (LeaderSupplement as LeaderApplication, 
                                     CrooSupplement, 
                                     GeneralApplication, LeaderApplicationGrade, 
                                     ApplicationInformation, CrooApplicationGrade,
                                     QualificationTag)
from doc.timetable.models import Timetable
from doc.trips.models import Section, ScheduledTrip


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

    def make_application(self, status=GeneralApplication.PENDING, trips_year=None):

        if trips_year is None:
            trips_year = self.current_trips_year

        application = mommy.make(GeneralApplication, 
                                 status=status,
                                 trips_year=trips_year)
        leader_app = mommy.make(LeaderApplication, 
                                application=application, 
                                trips_year=trips_year, 
                                document='some/file')
        croo_app = mommy.make(CrooSupplement, 
                              application=application, 
                              trips_year=trips_year, 
                              document='some/file')
        
        return application


class ApplicationAccessTestCase(ApplicationTestMixin, WebTestCase):

    def setUp(self):
        self.init_current_trips_year()

    def test_anonymous_user_does_not_crash_application(self):
        
        self.app.get(reverse('applications:apply'))
    def test_application_not_visible_if_not_available(self):
        
        self.close_application()
        self.mock_user()
        response = self.app.get(reverse('applications:apply'), user=self.user)
        self.assertTemplateUsed('applications/not_available.html')


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
                             

    def test_available_sections_in_leader_form_are_for_current_trips_year(self):

        prev_section = mommy.make(Section, trips_year=self.previous_trips_year)
        curr_section = mommy.make(Section, trips_year=self.current_trips_year)

        self.open_application()
        self.mock_user()

        response = self.app.get(reverse('applications:apply'), user=self.user)
        form = response.context['leader_form']
        self.assertEquals(list(form.fields['available_sections'].queryset),
                          list(Section.objects.filter(trips_year=self.current_trips_year)))
        self.assertEquals(list(form.fields['preferred_sections'].queryset),
                          list(Section.objects.filter(trips_year=self.current_trips_year)))


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
        
        application = self.make_application()
        application.leader_supplement.document = ''
        application.leader_supplement.save()

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
        
        application = self.make_application(status=GeneralApplication.LEADER)
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'only PENDING apps should be gradable')


    def test_can_only_grade_applications_for_the_current_trips_year(self):
        
        application = self.make_application(trips_year=self.previous_trips_year)
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'should not be able to grade apps from previous years')

    
    def test_correct_number_of_grades(self):

        application = self.make_application()

        for i in range(LeaderApplication.NUMBER_OF_GRADES):

            # works because we are not actually grading with self.user
            next = LeaderApplication.objects.next_to_grade(self.user)
            self.assertEquals(next, application.leader_supplement)
            
            grade = mommy.make(LeaderApplicationGrade, trips_year=self.trips_year,
                               application=application.leader_supplement)
           
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'can only grade NUMBER_OF_GRADES times')


class LeaderApplicationManager_prospectve_leaders_TestCase(ApplicationTestMixin, TripsTestCase):

    def setUp(self):
        self.init_current_trips_year()

    def test_prospective_leader_with_preferred_choices(self):

        trip = mommy.make(ScheduledTrip, trips_year=self.current_trips_year)
        
        app = self.make_application(status=GeneralApplication.LEADER)
        app.leader_supplement.preferred_sections.add(trip.section)
        app.leader_supplement.preferred_triptypes.add(trip.template.triptype)
        app.save()

        prospects = LeaderApplication.objects.prospective_leaders_for_trip(trip)
        self.assertEquals(list(prospects), [app.leader_supplement])

    def test_prospective_leader_with_available_choices(self):

        trip = mommy.make(ScheduledTrip, trips_year=self.current_trips_year)
        
        app = self.make_application(status=GeneralApplication.LEADER_WAITLIST)
        app.leader_supplement.available_sections.add(trip.section)
        app.leader_supplement.available_triptypes.add(trip.template.triptype)
        app.save()

        prospects = LeaderApplication.objects.prospective_leaders_for_trip(trip)
        self.assertEquals(list(prospects), [app.leader_supplement])

    def test_with_pending_status(self):
        trip = mommy.make(ScheduledTrip, trips_year=self.current_trips_year)
        
        # otherwise available
        app = self.make_application(status=GeneralApplication.PENDING)
        app.leader_supplement.preferred_sections.add(trip.section)
        app.leader_supplement.preferred_triptypes.add(trip.template.triptype)
        app.save()

        prospects = LeaderApplication.objects.prospective_leaders_for_trip(trip)
        self.assertEquals(list(prospects), [])

    def test_without_section_preference(self):
        
        trip = mommy.make(ScheduledTrip, trips_year=self.current_trips_year)
        
        # otherwise available
        app = self.make_application(status=GeneralApplication.LEADER)
        app.leader_supplement.preferred_triptypes.add(trip.template.triptype)
        app.save()

        prospects = LeaderApplication.objects.prospective_leaders_for_trip(trip)
        self.assertEquals(list(prospects), [])

    def test_without_triptype_preference(self):

        trip = mommy.make(ScheduledTrip, trips_year=self.current_trips_year)
       
        app = self.make_application(status=GeneralApplication.LEADER)
        app.leader_supplement.preferred_sections.add(trip.section)
        app.save()

        prospects = LeaderApplication.objects.prospective_leaders_for_trip(trip)
        self.assertEquals(list(prospects), [])

    def test_prospective_leaders_are_distinct(self):

        trip = mommy.make(ScheduledTrip, trips_year=self.current_trips_year)
       
        # set up a situation where JOINS will return the same app multiple times
        app = self.make_application(status=GeneralApplication.LEADER)
        app.leader_supplement.preferred_sections.add(trip.section)
        app.leader_supplement.available_sections.add(trip.section)
        app.leader_supplement.preferred_triptypes.add(trip.template.triptype)
        app.leader_supplement.available_triptypes.add(trip.template.triptype)
        app.save()

        prospects = LeaderApplication.objects.prospective_leaders_for_trip(trip)
        self.assertEquals(len(prospects), 1)
        self.assertEquals(list(prospects), [app.leader_supplement])
       

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
            res = self.app.get(reverse(view), user=self.director)
            self.assertTemplateUsed('applications/grading_not_available.html')
    
    def test_gradable_after_application_deadline(self):
        
        self.close_application() # puts deadline in the past 
        for view in self.grade_views:
            res = self.app.get(reverse(view), user=self.director)
            self.assertTemplateNotUsed('applications/grading_not_available.html')


class GradeForSpecificCrooTestCase(ApplicationTestMixin, WebTestCase):
    
    def setUp(self):
        self.init_current_trips_year()
        self.mock_director()

    def test_redirect_to_next_for_qualification_does_not_break(self):
        
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
        
        
                           
