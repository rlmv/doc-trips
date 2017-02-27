import random

from django.db import models
from django.db.models import Q

from fyt.db.models import TripsYear
from fyt.utils.choices import AVAILABLE, PREFER


# TODO: refactor grade choices to query off the GeneralApplication

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

        # Manually choose random element because .order_by('?') is buggy
        # See https://code.djangoproject.com/ticket/26390
        cnt = apps.count()
        if cnt > 0:
            return apps[random.randrange(0, cnt)]
        return None


class LeaderApplicationManager(ApplicationManager):

    def completed_applications(self, trips_year):
        return (self.filter(trips_year=trips_year)
                    .annotate(models.Count('application__answer'))
                    .exclude(application__answer__answer="")
                    .filter(application__answer__count=question_count(trips_year))
                    .filter(application__leader_willing=True))


class CrooApplicationManager(ApplicationManager):

    def completed_applications(self, trips_year):
        return (self.filter(trips_year=trips_year)
                    .annotate(models.Count('application__answer'))
                    .exclude(application__answer__answer="")
                    .filter(application__answer__count=question_count(trips_year))
                    .filter(application__croo_willing=True))

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


class GeneralApplicationManager(models.Manager):

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
                leader_supplement__leadertriptypechoice__preference__in=opts))

    def _with_answer_count(self, trips_year):
        """
        Annotates the applications with `answer__count`, the number of
        answers that the application has.
        """
        return self.filter(trips_year=trips_year).annotate(models.Count('answer'))

    def _with_all_answers(self, trips_year):
        """
        Applications with all answers complete.
        """
        return (self._with_answer_count(trips_year)
                    .exclude(answer__answer="")
                    .filter(answer__count=question_count(trips_year)))

    def idea(self, trips_year):
        questions = Question.objects.filter(
            trips_year=trips_year, type__in=[Question.LEADER, Question.ALL])

        query = Q(leader_willing=False)
        for q in questions:
            query |= (Q(answer__answer="") & Q(answer__question=q))

        return self.filter(trips_year=trips_year).filter(query)

    def leader_applications(self, trips_year):
        from .models import Question
        questions = Question.objects.filter(
            trips_year=trips_year, type__in=[Question.LEADER, Question.ALL])

        qs = self.filter(trips_year=trips_year, leader_willing=True)

        for question in questions:
            qs = qs.filter(Q(answer__question=question) & ~Q(answer__answer=""))

        return qs

    def croo_applications(self, trips_year):
        from .models import Question
        questions = Question.objects.filter(
            trips_year=trips_year, type__in=[Question.CROO, Question.ALL])

        qs = self.filter(trips_year=trips_year, croo_willing=True)

        for question in questions:
            qs = qs.filter(Q(answer__question=question) & ~Q(answer__answer=""))

        return qs

    # NOTE: There's a bug in Django (https://code.djangoproject.com/ticket/26959
    # and https://code.djangoproject.com/ticket/26522) which causes non-
    # deterministic failures when `|`ing together the leader and croo
    # querysets so we have to use this instead.
    def leader_or_croo_applications(self, trips_year):
        """
        Return all applications which have either the leader or croo section
        complete.
        """
        leader_pks = pks(self.leader_applications(trips_year))
        croo_pks = pks(self.croo_applications(trips_year))

        return self.filter(trips_year=trips_year).filter(
            Q(pk__in=leader_pks) | Q(pk__in=croo_pks))

    def leader_and_croo_applications(self, trips_year):
        return (self.leader_applications(trips_year) &
                self.croo_applications(trips_year))

    # TODO: is this how we should define incomplete applications?

    def incomplete_leader_applications(self, trips_year):
        leader_pks = pks(self.leader_applications(trips_year))
        return self.filter(trips_year=trips_year).exclude(pk__in=leader_pks)

    def incomplete_croo_applications(self, trips_year):
        croo_pks = pks(self.croo_applications(trips_year))
        return self.filter(trips_year=trips_year).exclude(pk__in=croo_pks)

    def leaders(self, trips_year):
        return self.filter(trips_year=trips_year, status=self.model.LEADER)

    def croo_members(self, trips_year):
        return self.filter(trips_year=trips_year, status=self.model.CROO)


def pks(qs):
    """
    Return the primary keys of a queryset.
    """
    return qs.values_list('pk', flat=True)


def question_count(trips_year):
    from .models import Question
    return Question.objects.filter(trips_year=trips_year).count()
