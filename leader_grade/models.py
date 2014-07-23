
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from leader.models import LeaderApplication


def validate_grade(min, max):
    def validate(grade):
        if grade < min or grade > max:
            raise ValidationError('grade is not in required range [{}, {}]'
                                  .format(min, max))
    return validate


class LeaderGrade(models.Model):

    MIN_GRADE = 0
    MAX_GRADE = 5

    grader = models.ForeignKey(settings.AUTH_USER_MODEL)
    leader_application = models.ForeignKey(LeaderApplication, related_name='grades')
    grade = models.DecimalField(max_digits=3, decimal_places=2, 
                                validators=[validate_grade(MIN_GRADE, MAX_GRADE)])
    comment = models.CharField(max_length=255)
    hard_skills = models.BooleanField(default=False)
    soft_skills = models.BooleanField(default=False)

    
