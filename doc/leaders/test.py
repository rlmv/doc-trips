
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from model_mommy import mommy

from test.fixtures import TripsYearTestCase as TripsTestCase, WebTestCase
from doc.trips.models import Section
from leaders.models import LeaderGrade, LeaderApplication
from leaders.views import *

class GradeValidationTestCase(TripsTestCase):

    def test_grade_validation(self):

        bad_grade = mommy.make('LeaderGrade', grade=LeaderGrade.MIN_GRADE-1)
                               
        with self.assertRaises(ValidationError):
            bad_grade.clean_fields()

        bad_grade.grade = LeaderGrade.MAX_GRADE + 1
        with self.assertRaises(ValidationError):
            bad_grade.clean_fields()

        good_grade = mommy.make('LeaderGrade', 
                                grade=(LeaderGrade.MIN_GRADE + LeaderGrade.MAX_GRADE) / 2)
        good_grade.clean_fields()


class LeaderApplicationManagerTestCase(TripsTestCase):

    def setUp(self):
        self.init_current_trips_year()
        self.init_previous_trips_year()
        
        self.user = mommy.make(get_user_model())
        self.user.save()

    def test_with_no_grades(self):

        application = mommy.make('LeaderApplication', 
                                 status=LeaderApplication.PENDING, 
                                 trips_year=self.trips_year)
        application.save()

        # no LeaderGrades with foreign key set to this app exist
        self.assertListEqual(list(application.grades.all()), [])
        
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertEqual(application, next)

    def test_graded_ungraded_priority(self):

        grade1 = mommy.make('LeaderGrade', 
                            leader_application__status=LeaderApplication.PENDING,
                            trips_year=self.trips_year)
        app1 = grade1.leader_application
        app2 = mommy.make('LeaderApplication', status=LeaderApplication.PENDING, 
                          trips_year=self.trips_year)

        app1.save()
        app2.save()
        
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertEqual(next, app2, 'app with no grades should have prio')

    def test_user_can_only_grade_application_once(self):
        
        grade1 = mommy.make('LeaderGrade', grader=self.user, 
                            leader_application__status=LeaderApplication.PENDING,
                            trips_year=self.trips_year)
        grade1.save()
        grade1.leader_application.save()
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'no applications should be available')

    def test_only_grade_pending_applications(self):
        
        application = mommy.make(LeaderApplication, 
                                 status=LeaderApplication.ACCEPTED,
                                 trips_year=self.trips_year)
        application.save()
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'ACCEPTED (or any status except PENDING) should not be gradable')

    def test_can_only_grade_applications_for_the_current_trips_year(self):
        
        application = mommy.make(LeaderApplication, status=LeaderApplication.PENDING,
                                 trips_year=self.previous_trips_year)
        application.save()
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'should not be able to grade apps from previous years')



class ApplicationGraderViewsTestCase(WebTestCase):

    # TODO: test that non-graders are redirected to login

    csrf_checks = False

    def setUp(self):
        self.init_current_trips_year()
        self.init_old_trips_year()

    def test_grader_redirects(self):

        self.mock_grader()
        
        app = mommy.make('LeaderApplication', status=LeaderApplication.PENDING,
                         trips_year=self.trips_year)

        response = self.app.get(reverse('leaders:grade_random'), user=self.grader)
        response = response.follow()
        self.assertEquals(app, response.context['leaderapplication'])

        # grade the app
        grade = mommy.make('LeaderGrade', grader=self.grader, leader_application=app)

        # there should be no more applications to grade
        response = self.app.get(reverse('leaders:grade_random'), user=self.grader)
        response = response.follow()
        self.assertEquals(response.templates[0].name, 'leader/no_application.html')


    def test_grading_application_adds_trips_year_to_grade(self):

        self.mock_grader()

        application = mommy.make(LeaderApplication, status=LeaderApplication.PENDING,
                                 trips_year=self.trips_year)
        response = self.app.post(reverse('leaders:grade', kwargs={'pk': application.pk }), 
                                 {'grade': 3,
                                  'comment': 'test grade comment'}, 
                                 user=self.grader)

        grade = LeaderGrade.objects.get(leader_application=application)
        self.assertEquals(grade.trips_year, self.trips_year)


class LeaderApplicationViewsTestCase(WebTestCase):

    # TODO: test that non-graders are redirected to login

    csrf_checks = False

    def setUp(self):
        self.init_current_trips_year()
        self.init_old_trips_year()


    def test_applying_adds_the_current_trips_year_and_user_to_model(self):
        
        self.mock_user()

        data = model_to_dict(mommy.prepare(LeaderApplication), fields=LeaderApply.fields)
        response = self.app.post(reverse('leaders:apply'), data, user=self.user)
        
        # TODO: test redirects
        #self.assertEquals(response.status_code, 200)
        
        application = LeaderApplication.objects.all()[0]
        # should add user and current trips_year
        self.assertEquals(self.user, application.user)
        self.assertEquals(self.trips_year, application.trips_year)
        
    
    def test_application_flow(self):

        self.mock_user()

        response = self.app.get(reverse('leaders:apply'), user=self.user)
        self.assertEquals(response.status_code, 200)
    
        app_data = model_to_dict(mommy.prepare(LeaderApplication), fields=LeaderApply.fields)       
        response = self.app.post(reverse('leaders:apply'), app_data, user=self.user)
        response = response.follow()

        self.assertEquals(response.status_code, 200)

    
    def test_applying_and_revisiting_pages_allows_user_to_edit_application(self):
        
        self.mock_user()

        data = model_to_dict(mommy.prepare(LeaderApplication), 
                             fields=LeaderApply.fields)
        response = self.app.post(reverse('leaders:apply'), data, user=self.user)
        response = self.app.get(reverse('leaders:apply'), user=self.user)
        application = response.context['object']
        
        # should see previous application
        self.assertIsNotNone(application)
        self.assertEquals(data['class_year'], application.class_year)

    
    def test_available_sections_in_application_form_are_only_for_current_trips_year(self):
        self.mock_user()

        prev_section = mommy.make('Section', trips_year=self.previous_trips_year)
        curr_section = mommy.make('Section', trips_year=self.current_trips_year)

        response = self.app.get(reverse('leaders:apply'), user=self.user)
        form = response.context['form']

        self.assertEquals(list(form.fields['available_sections'].queryset),
                          list(Section.objects.filter(trips_year=self.current_trips_year)))
        self.assertEquals(list(form.fields['preferred_sections'].queryset),
                          list(Section.objects.filter(trips_year=self.current_trips_year)))
        

    def test_application_is_not_available_if_not_in_calendar_dates(self):

        # close leader applications:
        from doc.timetable.models import Timetable
        from datetime import timedelta
        t = Timetable.objects.timetable()
        t.leader_application_open += timedelta(-2)
        t.leader_application_closed += timedelta(-1)
        t.save()

        self.mock_user()
        response = self.app.get(reverse('leaders:apply'), user=self.user)
        self.assertTemplateUsed('leader/application_not_available.html')

        







        
        
        
        
        
        
        
                       

    
                              
                                   

