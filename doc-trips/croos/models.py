
from django.conf import settings
from django.db import models

from db.models import DatabaseModel, TripsYear


class CrooApplicationQuestion(DatabaseModel):

    class Meta: 
        ordering = ['ordering']
    
    question = models.TextField()
    ordering = models.IntegerField()


class CrooApplicationAnswer(DatabaseModel):

    class Meta:
        ordering = ['question__ordering']

    answer = models.TextField()
    # editable=False?
    question = models.ForeignKey(CrooApplicationQuestion)
    application = models.ForeignKey('CrooApplication', 
                                    related_name='answers', 
                                    editable=False)


class CrooApplicationManager(models.Manager):

    """ Directly translated from the LeaderApplicationManager. """

    def next_to_grade(self, grader):

        trips_year = TripsYear.objects.current()

        # Each croo app is graded blind three times
        application = self._get_random_application(grader, trips_year, 0)
        if not application:
            application = self._get_random_application(grader, trips_year, 1)
        if not application:
            application = self._get_random_application(grader, trips_year, 2)
        
        return application


    def _get_random_application(self, grader, trips_year, num):
        """ Return a random application, which 'grader' has not graded, 
        and has only been graded by num people."""
        
        application = (self.filter(trips_year=trips_year)
                       .filter(status=self.model.PENDING)
                       .annotate(models.Count('grades'))
                       .filter(grades__count=num)
                       .exclude(grades__grader=grader)
                       .order_by('?')[:1]) # this may be expensive
        
        return application[0] if application else None
    
    
class CrooApplication(DatabaseModel):

    objects = CrooApplicationManager()
    
    
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

    assigned_croo = models.ForeignKey('Croo', blank=True, null=True, 
                                      related_name='croolings',
                                      on_delete=models.SET_NULL)
    potential_croos = models.ManyToManyField('Croo', blank=True, 
                                             related_name='potential_croolings')

    safety_dork_qualified = models.BooleanField(default=False)
    safety_dork = models.BooleanField(default=False)

    def __str__(self):
        return self.applicant.name


class Croo(DatabaseModel):
    """
    Represents a croo organization. 

    Migrates each year.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    

class CrooApplicationGrade(DatabaseModel):
    
    grader = models.ForeignKey(settings.AUTH_USER_MODEL, )
    application = models.ForeignKey(CrooApplication, related_name='grades')
    grade = models.IntegerField()
    comments = models.TextField()



    
