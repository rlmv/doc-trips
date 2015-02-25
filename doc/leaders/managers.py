
from django.db import models

from doc.db.models import TripsYear

class LeaderApplicationManager(models.Manager):
    
    def next_to_grade(self, user):
        """ Find the next leader application to grade for user.

        This is an application which meets the following conditions:
        (0) is for the current trips_year
        (1) has not yet been graded if there are apps in the database
        which have not been graded, otherwise an application with only 
        one grade.
        (2) has not already been graded by this user
        (3) the application is not disqualified, deprecated, etc. See
        LeaderApplication status field. It should be PENDING.
        """

        trips_year = TripsYear.objects.current()

        application = self._get_random_application(user, trips_year, 0)
        if not application:
            application = self._get_random_application(user, trips_year, 1)

        return application


    def _get_random_application(self, user, trips_year, num):
        """ Return a random PENDING application that user has not graded, 
        which has only been graded by num people. """
        
        application = (self.filter(status=self.model.PENDING)
                       .filter(trips_year=trips_year)
                       .annotate(models.Count('grades'))
                       .filter(grades__count=num)
                       .exclude(grades__grader=user)
                       # random database-level ordering. 
                       # TODO: this may be expensive?
                       .order_by('?')[:1])
        
        return application[0] if application else None
    



    
