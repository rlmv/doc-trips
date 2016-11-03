import random

from django.db import models
from django.db.models import Q

from fyt.db.models import TripsYear
from fyt.utils.choices import PREFER, AVAILABLE


class ApplicationManager(models.Manager):
    """
    Shared manager for Leader and Croo grades

    Requires model to have a NUMBER_OF_GRADES property which
    specifies how many times the application should be graded.
    """

    def next_to_grade(self, user):
        """
        Find the next application to grade for user.

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
        from fyt.applications.models import GeneralApplication
        PENDING = GeneralApplication.PENDING

        apps = (self.completed_applications(trips_year=trips_year).
                filter(application__status=PENDING)
                .exclude(grades__grader=user)
                .exclude(skips__grader=user)
                .annotate(grade_count=models.Count('grades'))
                .filter(grade_count=num))

        # choose random element manually
        # .order_by('?') is buggy in 1.8
        cnt = apps.count()
        if cnt > 0:
            return apps[random.randrange(0, cnt)]
        return None

    def completed_applications(self, trips_year):
        return self.filter(trips_year=trips_year).exclude(document='')


class LeaderApplicationManager(ApplicationManager):

    pass


class CrooApplicationManager(ApplicationManager):

      def next_to_grade_for_qualification(self, user, qualification):
        """
        Find the next croo application which has qualification
        for user to grade.

        We're just serving apps for the specified qualification
        and don't care about limits to the total number of grades.
        If the grader skipped an app in regular grading we still
        include if.
        However, if the grader skipped an app while grading for
        this qualification we exclude it from the the query.

        TODO: pass in the trips year? - tie grading to a trips_year url?
        TODO: tests for the manager in addition to the view tests

        Return None if no applications need to be graded.
        """

        trips_year = TripsYear.objects.current()

        # grab the value of GeneralApplication.PENDING
        from fyt.applications.models import GeneralApplication
        PENDING = GeneralApplication.PENDING

        return (self.completed_applications(trips_year=trips_year)
                .filter(grades__qualifications=qualification)
                .filter(application__status=PENDING)
                # satisfy BOTH condifions for the same skip:
                .exclude(skips__grader=user,
                         skips__for_qualification=qualification)
                .exclude(grades__grader=user)
                .order_by('?').first())



class GeneralApplicationManager(models.Manager):\

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('applicant', 'croo_supplement',
                                 'leader_supplement')

    def prospective_leaders_for_trip(self, trip):
        """
        Get prospective leaders who can lead Trip trip.

        Returns all GeneralApplications which
        (1) are for the same trips_year as trip
        (2) are complete
        (3) prefer or are available for trip's TripType and Section

        We don't exclude leaders already assigned to a trip.
        """

        triptype = trip.template.triptype
        opts = [PREFER, AVAILABLE]

        return (
            self.leader_applications(trip.trips_year)
            .filter(
                leader_supplement__leadersectionchoice__section=trip.section,
                leader_supplement__leadersectionchoice__preference__in=opts)
            .filter(
                leader_supplement__leadertriptypechoice__triptype=triptype,
                leader_supplement__leadertriptypechoice__preference__in=opts)
        )

    def leader_applications(self, trips_year):
        return self.filter(trips_year=trips_year).exclude(leader_supplement__document="")

    def croo_applications(self, trips_year):
        return self.filter(trips_year=trips_year).exclude(croo_supplement__document="")

    def leader_or_croo_applications(self, trips_year):
        """ Return all GenApps with either complete croo OR tl parts """
        return (self.filter(trips_year=trips_year)
                .exclude(Q(leader_supplement__document="") &
                         Q(croo_supplement__document="")))

    def incomplete_leader_applications(self, trips_year):
        return self.filter(trips_year=trips_year, leader_supplement__document="")

    def incomplete_croo_applications(self, trips_year):
        return self.filter(trips_year=trips_year, croo_supplement__document="")

    def leaders(self, trips_year):
        return self.filter(trips_year=trips_year, status=self.model.LEADER)

    def croo_members(self, trips_year):
        return self.filter(trips_year=trips_year, status=self.model.CROO)
