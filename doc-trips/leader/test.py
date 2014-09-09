
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from model_mommy import mommy

from test.fixtures import TestCase
from leader.models import LeaderGrade, LeaderApplication
from leader.views import *

class GradeValidationTestCase(TestCase):

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


class LeaderApplicationManagerTestCase(TestCase):

    def setUp(self):
        self.init_current_trips_year()
        
        self.user = mommy.make('User')
        self.user.save()

    def test_with_no_grades(self):

        application = mommy.make('LeaderApplication', 
                                 status=LeaderApplication.PENDING)
        application.save()

        # no LeaderGrades with foreign key set to this app exist
        self.assertListEqual(list(application.grades.all()), [])
        
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertEqual(application, next)

    def test_graded_ungraded_priority(self):

        grade1 = mommy.make('LeaderGrade', 
                            leader_application__status=LeaderApplication.PENDING)    
        app1 = grade1.leader_application
        app2 = mommy.make('LeaderApplication', status=LeaderApplication.PENDING)

        app1.save()
        app2.save()
        
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertEqual(next, app2, 'app with no grades should have prio')

    def test_user_can_only_grade_application_once(self):
        
        grade1 = mommy.make('LeaderGrade', grader=self.user, 
                            leader_application__status=LeaderApplication.PENDING)
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'no applications should be available')

    def test_only_grade_pending_applications(self):
        
        application = mommy.make(LeaderApplication, 
                                 status=LeaderApplication.ACCEPTED)
        next = LeaderApplication.objects.next_to_grade(self.user)
        self.assertIsNone(next, 'ACCEPTED (or any status except PENDING) should not be gradable')


class ApplicationViewsTestCase(TestCase):

    # TODO: test that non-graders are redirected to login

    def test_redirects(self):

        self.mock_grader_login()
        
        app = mommy.make('LeaderApplication', status=LeaderApplication.PENDING)
        app.save()
        response = self.client.get(reverse('leader:grade_random'), follow=True)
        self.assertEquals(app, response.context['leaderapplication'])

        # grade the app
        grade = mommy.make('LeaderGrade', grader=self.grader, leader_application=app)
        grade.save()

        # there should be no more applications to grade
        response = self.client.get(reverse('leader:grade_random'), follow=True)
        self.assertEquals(response.templates[0].name, 'leader/no_application.html')
        
                       

    
                              
                                   

