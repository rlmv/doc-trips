import random

from django.db import models
from django.db.models import Case, Lookup, Q, When
from django.db.models.fields import Field

from fyt.db.models import TripsYear
from fyt.permissions import permissions
from fyt.users.models import DartmouthUser
from fyt.utils.choices import AVAILABLE, PREFER


# TODO: refactor grade choices to query off the Volunteer


@Field.register_lookup
class NotEqual(Lookup):
    """
    Register a not-equals lookup.
    """
    lookup_name = 'ne'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params


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
        Volunteer status field. It should be PENDING.

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

        Note that the status lives on the parent Volunteer object.
        """
        # grab the value of Volunteer.PENDING
        from fyt.applications.models import Volunteer
        PENDING = Volunteer.PENDING

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
        from .models import Volunteer
        leader_applications = Volunteer.objects.leader_applications(trips_year)

        return self.filter(application__pk__in=pks(leader_applications))


class CrooApplicationManager(ApplicationManager):

    def completed_applications(self, trips_year):
        from .models import Volunteer
        croo_applications = Volunteer.objects.croo_applications(trips_year)

        return self.filter(application__pk__in=pks(croo_applications))

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

        # grab the value of Volunteer.PENDING
        from fyt.applications.models import Volunteer
        PENDING = Volunteer.PENDING

        return (self.completed_applications(trips_year=trips_year)
                .filter(grades__qualifications=qualification)
                .filter(application__status=PENDING)
                # satisfy BOTH condifions for the same skip:
                .exclude(skips__grader=user,
                         skips__for_qualification=qualification)
                .exclude(grades__grader=user)
                .order_by('?').first())


class VolunteerManager(models.Manager):

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('applicant', 'croo_supplement',
                                 'leader_supplement')

    def prospective_leaders_for_trip(self, trip):
        """
        Get prospective leaders who can lead Trip trip.

        Returns all Volunteers which
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

    def leader_applications(self, trips_year):
        from .models import Question
        questions = Question.objects.for_leaders(trips_year)

        qs = self.filter(trips_year=trips_year, leader_willing=True)

        for question in questions:
            qs = qs.filter(answer__question=question, answer__answer__ne="")

        return qs

    def croo_applications(self, trips_year):
        from .models import Question
        questions = Question.objects.for_croos(trips_year)

        qs = self.filter(trips_year=trips_year, croo_willing=True)

        for question in questions:
            qs = qs.filter(answer__question=question, answer__answer__ne="")

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

        either_pks = set(leader_pks).union(croo_pks)

        return self.filter(trips_year=trips_year).filter(pk__in=either_pks)

    # NOTE: the same bug affects ANDs as well
    def leader_and_croo_applications(self, trips_year):
        leader_pks = pks(self.leader_applications(trips_year))
        croo_pks = pks(self.croo_applications(trips_year))

        shared_pks = set(leader_pks) & set(croo_pks)

        return self.filter(trips_year=trips_year).filter(pk__in=shared_pks)

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

    def next_to_score(self, grader):
        """
        Return the next application for ``grader`` to score.

        This is an application which meets the following conditions:

        * is for the current trips_year
        * is complete
        * is PENDING
        * has not already been graded by this user
        * has not been skipped by this user
        * has been graded fewer than NUM_SCORES times

        Furthermore:
        * If the grader is not a croo captain, don't add the last score to an
          app which hasn't been scored by a croo captain; that is, every croo
          application must be graded at least once by a croo captain.
        * If the grader is a croo captain, prefer croo grades until each app
          has at least one score from a croo head.
        """
        trips_year = TripsYear.objects.current()

        croo_app_pks = self.croo_applications(trips_year)

        NUM_SCORES = self.model.NUM_SCORES

        qs = self.leader_or_croo_applications(
            trips_year=trips_year
        ).filter(
            status=self.model.PENDING
        ).exclude(
            scores__grader=grader
        ).exclude(
            skips__grader=grader
        ).annotate(
            models.Count('scores')
        ).filter(
            scores__count__lt=NUM_SCORES
        ).annotate(
            has_croo_head_score=TrueIf(scores__croo_head=True)
        ).annotate(
            is_croo_application=TrueIf(pk__in=croo_app_pks)
        )

        # Croo head: try and pick a croo app which needs a croo head score
        if grader.has_perm('permissions.can_grade_as_croo_head'):
            needs_croo_head_score = qs.filter(
                has_croo_head_score=False,
                is_croo_application=True)

            if needs_croo_head_score.first():
                qs = needs_croo_head_score

        # Otherwise, reserve one score on each app for a croo head
        else:
            qs = qs.filter(
                scores__count__lt=Case(
                    When(is_croo_application=True,
                         has_croo_head_score=False,
                         then=(NUM_SCORES - 1)),
                    default=NUM_SCORES
                )
            )
        return qs.first()


def TrueIf(**kwargs):
    """
    Return a case expression that evaluates to True if the query conditions
    are met, else False
    """
    return Case(
        When(then=True, **kwargs),
        default=False,
        output_field=models.BooleanField()
    )


def pks(qs):
    """
    Return the primary keys of a queryset.
    """
    return qs.values_list('pk', flat=True)


class QuestionManager(models.Manager):

    def for_leaders(self, trips_year):
        target_types = [self.model.LEADER, self.model.ALL]
        return self.filter(trips_year=trips_year).filter(type__in=target_types)

    def for_croos(self, trips_year):
        target_types = [self.model.CROO, self.model.ALL]
        return self.filter(trips_year=trips_year).filter(type__in=target_types)
