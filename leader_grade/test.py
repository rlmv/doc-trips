
from django.test import TestCase
from django.core.exceptions import ValidationError

from model_mommy import mommy

from .models import LeaderGrade
from .views import get_next_application_to_grade

class GradeValidationTestCase(TestCase):

    def test_grade_validation(self):

        bad_grade = mommy.make('LeaderGrade', grade=LeaderGrade.MIN_GRADE-1)
        with self.assertRaises(ValidationError):
            bad_grade.clean_fields()

        bad_grade.grade = LeaderGrade.MAX_GRADE + 1
        with self.assertRaises(ValidationError):
            bad_grade.clean_fields()

        good_grade = mommy.make('LeaderGrade', grade=(LeaderGrade.MIN_GRADE + LeaderGrade.MAX_GRADE) / 2)
        good_grade.clean_fields()


class GetNextApplicationToGradeTestCase(TestCase):

    def setUp(self):
        self.user = mommy.make('User')
        self.user.save()

    def test_with_no_grades(self):

        application = mommy.make('LeaderApplication')
        application.save()

        # no LeaderGrades with foreign key set to this app exist
        self.assertListEqual(list(application.leadergrade_set.all()), [])
        
        next = get_next_application_to_grade(self.user)
        self.assertEqual(application, next)

    def test_graded_ungraded_priority(self):

        grade1 = mommy.make('LeaderGrade')    
        app1 = grade1.leader_application
        app2 = mommy.make('LeaderApplication')

        app1.save()
        app2.save()
        
        next = get_next_application_to_grade(self.user)
        self.assertEqual(next, app2, 'app with no grades should have prio')

    def test_user_can_only_grade_application_once(self):
        
        grade1 = mommy.make('LeaderGrade', grader=self.user)
        next = get_next_application_to_grade(self.user)
        self.assertIsNone(next, 'no applications should be available')
        
        
        

