
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from doc.db.models import DatabaseModel, TripsYear


class CrooApplicationQuestion(DatabaseModel):

    class Meta: 
        ordering = ['ordering']
    
    question = models.TextField()
    ordering = models.IntegerField()


class CrooApplicationAnswer(DatabaseModel):

    class Meta:
        ordering = ['question__ordering']

    answer = models.TextField(blank=True)
    # editable=False?
    question = models.ForeignKey(CrooApplicationQuestion)
    application = models.ForeignKey('CrooApplication', 
                                    related_name='answers', 
                                    editable=False)

    
class CrooApplication(DatabaseModel):
    
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL)

    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    CANCELED = 'CANCELED'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (CANCELED, 'Cancelled')
    )
    status = models.CharField('Application status', max_length=10, 
                              choices=STATUS_CHOICES, default=PENDING)

#    assigned_croo = models.ForeignKey('Croo', blank=True, null=True, 
#                                      related_name='croolings',
#                                      on_delete=models.SET_NULL)
#    potential_croos = models.ManyToManyField('Croo', blank=True, 
#                                             related_name='potential_croolings')

    safety_dork_qualified = models.BooleanField(default=False)
    safety_dork = models.BooleanField(default=False)

    def average_grade(self):
        r = self.grades.all().aggregate(models.Avg('grade'))
        return r['grade__avg']
    
    def clean(self):
        """ If app is not ACCEPTED it cannot be assigned to croo """

        if self.status != self.ACCEPTED and self.assigned_croo:
            raise ValidationError("Croo Application cannot be assigned to a Croo. "
                                  "Change status to 'Accepted' or remove Croo")

    def __str__(self):
        return self.applicant.name


class Croo(DatabaseModel):
    """
    Represents a croo organization. 

    Migrates each year.
    """
    
    class Meta:
        ordering = ['name']
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    

def validate_grade(grade):
    """ Validator for CrooApplicationGrade.grade """

    if (grade < CrooApplicationGrade.MIN_GRADE or
        grade > CrooApplicationGrade.MAX_GRADE):
        raise ValidationError('grade must be in range {}-{}'.format(
            CrooApplicationGrade.MIN_GRADE, CrooApplicationGrade.MAX_GRADE))

class _CrooApplicationGrade(DatabaseModel):

    MIN_GRADE = 1
    MAX_GRADE = 6
    
    grader = models.ForeignKey(settings.AUTH_USER_MODEL)
    application = models.ForeignKey(CrooApplication, related_name='grades')
    grade = models.IntegerField(validators=[validate_grade])
    comments = models.TextField()



    
