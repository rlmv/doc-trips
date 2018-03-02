import random

from django.db import models
from django.db.models import (
    F,
    Q,
    Avg,
    Case,
    Count,
    Lookup,
    Min,
    Sum,
    Value as V,
    When,
)
from django.db.models.fields import Field
from django.db.models.functions import Coalesce

from fyt.core.models import TripsYear
from fyt.utils.choices import AVAILABLE, PREFER
from fyt.utils.query import pks


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
        questions = Question.objects.required_for_leaders(trips_year)

        qs = self.filter(trips_year=trips_year, leader_willing=True)

        for question in questions:
            qs = qs.filter(answer__question=question, answer__answer__ne="")

        return qs

    def croo_applications(self, trips_year):
        from .models import Question
        questions = Question.objects.required_for_croos(trips_year)

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

    def incomplete_leader_applications(self, trips_year):
        """
        Return all leader applications which are incomplete.
        """
        return self.filter(
            trips_year=trips_year,
            leader_willing=True
        ).exclude(
            pk__in=pks(self.leader_applications(trips_year))
        )

    def incomplete_croo_applications(self, trips_year):
        """
        Return all croo applications which are incomplete.
        """
        return self.filter(
            trips_year=trips_year,
            croo_willing=True
        ).exclude(
            pk__in=pks(self.croo_applications(trips_year))
        )

    def leaders(self, trips_year):
        return self.filter(trips_year=trips_year, status=self.model.LEADER)

    def croo_members(self, trips_year):
        return self.filter(trips_year=trips_year, status=self.model.CROO)

    def leader_waitlist(self, trips_year):
        return self.filter(trips_year=trips_year,
                           status=self.model.LEADER_WAITLIST)

    def with_scores(self, trips_year):
        """
        Return all applications for this year annotated with an `avg_score`
        and a `norm_avg_score`.

        Scores are coalesced into the normalized attribute so that, when
        ordering on Postgres, null values come after the actual scores.
        Note that this issue won't appear on a dev sqlite database.
        """
        return self.filter(
            trips_year=trips_year
        ).annotate(
            avg_score=Avg('scores__score')
        ).annotate(
            norm_avg_score=Coalesce('avg_score', V(0.0))
        )

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
        * If the grader is a croo captain, prefer croo grades until each app
          has at least one score from a croo head.
        * Applications with fewer graders are prioritized.

        TODO:
        * If the grader is not a croo captain, don't add the last score to an
          app which hasn't been scored by a croo captain; that is, every croo
          application must be graded at least once by a croo captain. This is
          currently not working because of what seems like a bug in the Django
          ORM.
        """
        trips_year = TripsYear.objects.current()

        croo_app_pks = pks(self.croo_applications(trips_year))

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
        )

        # Croo head: try and pick a croo app which needs a croo head score
        if grader.has_perm('permissions.can_score_as_croo_head'):
            needs_croo_head_score = qs.filter(
                Q(pk__in=croo_app_pks) & ~Q(scores__croo_head=True)
            )

            if needs_croo_head_score.first():
                qs = needs_croo_head_score

        # TODO: make this work
        # Otherwise, reserve one score on each app for a croo head
        # else:
        #     qs = qs.filter(scores__count__lt=NUM_SCORES)
        #     qs = qs.filter(
        #         scores__count__lt=Case(
        #             When(~Q(pk__in=croo_app_pks), then=NUM_SCORES),
        #             When(~Q(scores__croo_head=True), then=(NUM_SCORES - 1)),
        #             default=NUM_SCORES,
        #             output_field=models.IntegerField()
        #         )
        #     )

        # Pick an app with fewer scores
        # TODO: use a subquery
        qs = qs.filter(
            scores__count=qs.aggregate(fewest=Min('scores__count'))['fewest']
        )

        # Manually choose random element because .order_by('?') is buggy
        # See https://code.djangoproject.com/ticket/26390
        if qs.count() > 0:
            return random.choice(qs)

        return None

    def score_progress(self, trips_year):
        """
        Return a tuple containing the number of scores given so far for each
        application and the total number of scores required to fully grade
        all applications.

        This ignores scores more than NUM_SCORES per application.
        """
        NUM_SCORES = self.model.NUM_SCORES

        qs = self.leader_or_croo_applications(trips_year)

        total = qs.count() * NUM_SCORES

        complete = sum(
            min(x.scores__count, NUM_SCORES)
            for x in qs.annotate(Count('scores')))

        return {
            'complete': complete,
            'total': total,
            'percentage': round(complete / total * 100) if total else 100
        }


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


class QuestionManager(models.Manager):

    def required_for_leaders(self, trips_year):
        target_types = [self.model.LEADER, self.model.ALL]
        return self.required(trips_year).filter(type__in=target_types)

    def required_for_croos(self, trips_year):
        target_types = [self.model.CROO, self.model.ALL]
        return self.required(trips_year).filter(type__in=target_types)

    def required(self, trips_year):
        return self.filter(trips_year=trips_year, type__ne=self.model.OPTIONAL)
