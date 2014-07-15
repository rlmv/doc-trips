
from django.test import TestCase
from .models import LeaderGrade
from django.core.exceptions import ValidationError

class LeaderGradeTestCase(TestCase):

    def test_grade_validation(self):
        exclude = ['grader', 'leader_application', 'comment']
        
        bad_grade = LeaderGrade(grade=LeaderGrade.MIN_GRADE - 1)
        with self.assertRaises(ValidationError):
            bad_grade.clean_fields(exclude=exclude)

        bad_grade = LeaderGrade(grade=LeaderGrade.MAX_GRADE + 1)
        with self.assertRaises(ValidationError):
            bad_grade.clean_fields(exclude=exclude)

        good_grade = LeaderGrade(grade=(LeaderGrade.MIN_GRADE + LeaderGrade.MAX_GRADE) / 2)
        good_grade.clean_fields(exclude=exclude)

