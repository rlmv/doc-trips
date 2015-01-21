
from django.conf import settings
from django.db import models
from jsonfield import JSONField
from sortedm2m.fields import SortedManyToManyField

from db.models import DatabaseModel


class CrooApplicationQuestion(DatabaseModel):
    
    question = models.TextField()
    ordering = models.IntegerField()

class CrooApplicationAnswer(DatabaseModel):

    answer = models.TextField()
    # editable=False?
    question = models.ForeignKey(CrooApplicationQuestion)
    application = models.ForeignKey('CrooApplication', 
                                    related_name='answers', 
                                    editable=False)
    
    
class CrooApplication(DatabaseModel):

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL)

    assigned_croo = models.ForeignKey('Croo', blank=True, null=True, 
                                      related_name='croolings',
                                      on_delete=models.SET_NULL)
    potential_croos = models.ManyToManyField('Croo', blank=True, 
                                             related_name='potential_croolings')

    safety_dork_qualified = models.BooleanField(default=False)
    safety_dork = models.BooleanField(default=False)

class Croo(DatabaseModel):
    """
    Represents a croo organization. 

    Migrates each year.
    """
    name = models.CharField(max_length=255)

class CrooApplicationGrade(DatabaseModel):
    
    grader = models.ForeignKey(settings.AUTH_USER_MODEL)
    croo_application = models.ForeignKey(CrooApplication, related_name='grades')



    
