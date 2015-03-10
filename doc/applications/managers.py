
from django.db import models
from django.db.models import Q

from doc.db.models import TripsYear


class ApplicationManager(models.Manager):
    """
    Shared manager for Leader and Croo grades 

    Requires model to have a NUMBER_OF_GRADES property which 
    specifies how many times the application should be graded. 
    """
    
    def next_to_grade(self, user):
        """ Find the next application to grade for user.

        This is an application which meets the following conditions:
        (0) is for the current trips_year
        (1) has not yet been graded if there are apps in the database
        which have not been graded, otherwise an application with only 
        one grade.
        (2) has not already been graded by this user
        (3) the application is not qualified, deprecated, etc. See
        GeneralApplication status field. It should be PENDING.

        Return None if no applications need to be graded.
        """

        trips_year = TripsYear.objects.current()

        for i in range(self.model.NUMBER_OF_GRADES):
            application = self._get_random_application(user, trips_year, i)
            if application:
                return application

        return None


    def _get_random_application(self, user, trips_year, num):
        """ 
        Return a random PENDING application that user has not graded, 
        which has only been graded by num people. 

        Note that the status lives on the parent GeneralApplication object.
        """

        # grab the value of GeneralApplication.PENDING
        PENDING = self.model.application.field.related_field.model.PENDING

        return (self.completed_applications(trips_year=trips_year).
                filter(application__status=PENDING)
                .annotate(models.Count('grades'))
                .filter(grades__count__lte=num)
                .exclude(grades__grader=user)
                # random database-level ordering. 
                # TODO: this may be expensive?
                .order_by('?').first())

    def completed_applications(self, trips_year):
        return self.filter(trips_year=trips_year).exclude(document='')    



class LeaderApplicationManager(ApplicationManager):

    def prospective_leaders_for_trip(self, trip):
        """ 
        Get prospective leaders who can lead ScheduledTrip trip.
        
        Returns all LeaderApplications which 
        (1) are for the same trips_year as trip
        (2) are Accepted or Waitlisted as leaders
        (3) prefer or are available for trip's TripType and Section

        We don't exclude leaders already assigned to a trip.
        """

        LEADER = self.model.application.field.related_field.model.LEADER
        LEADER_WAITLIST = self.model.application.field.related_field.model.LEADER_WAITLIST

        return (self.filter(trips_year=trip.trips_year)
                .filter(Q(application__status=LEADER) |
                        Q(application__status=LEADER_WAITLIST))
                .filter(Q(preferred_sections=trip.section) | 
                        Q(available_sections=trip.section))
                .filter(Q(preferred_triptypes=trip.template.triptype) | 
                        Q(available_triptypes=trip.template.triptype))
                .distinct())
                           
        
        

    
