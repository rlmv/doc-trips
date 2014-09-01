

from django.db import models

class LeaderApplicationManager(models.Manager):
    
    def next_to_grade(self, user):
        """ Find the next leader application to grade for user.

        This is an application which meets the following conditions:
        (1) has not yet been graded if there are apps in the database
        which have not been graded, otherwise an application with only 
        one grade.
        (2) has not already been graded by this user
        (3) the application is not disqualified, deprecated, etc. See
        LeaderApplication status field. It should be PENDING.
        """

        application = self._get_random_application(user, 0)
        if not application:
            application = self._get_random_application(user, 1)

        return application


    def _get_random_application(self, user, num):
        """ Return a random PENDING application that user has not graded, 
        which has only been graded by num people. """
        
        application = (self.filter(status=self.model.PENDING)
                       .annotate(models.Count('grades'))
                       .filter(grades__count=num)
                       .exclude(grades__grader=user)
                       # random ordering. TODO: this may be expensive?
                       .order_by('?')[:1])
        
        return application[0] if application else None
    



    
