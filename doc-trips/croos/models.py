
from django.conf import settings
from django.db import models

from db.models import DatabaseModel


class CrooApplicationQuestions(DatabaseModel):
    # holds the application questions for each year
    # There is exactly one CrooApplicationQuestions instance for 
    # each trips_year.
    questions = JSONField()

    # TODO: uniqueness validation per year.


class Croo(DatabaseModel):
    """
    Represents a croo organization. 

    Migrates each year.
    """
    name = models.CharField(max_length=255)
    

class CrooApplication(DatabaseModel):

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL)
    answers = JsonField()
    assigned_croo = models.ForeignKey('Croo', blank=True, null=True, 
                                      related_name='croolings',
                                      on_delete=models.SET_NULL)


class CrooApplicationGrade(DatabaseModel):
    
    grader = models.ForeignKey(settings.AUTH_USER_MODEL)
    croo_application = models.ForeignKey(CrooApplication, related_name='grades')



    
