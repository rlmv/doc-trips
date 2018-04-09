from collections import OrderedDict

from django.db import models
from django.db.models import Lookup, Avg, Value as V, Case, Count, Sum, When
from django.db.models.fields import Field
from django.db.models.functions import Coalesce
from django.utils import timezone

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


class BaseVolunteerManager(models.Manager):

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
        Return all applications for this year annotated with
        `avg_leader_score`, `norm_avg_leader_score`, `avg_croo_score`,
        `norm_avg_croo_score`.

        Scores are coalesced into the normalized attribute so that, when
        ordering on Postgres, null values come after the actual scores.
        Note that this issue won't appear on a dev sqlite database.
        """
        return self.filter(
            trips_year=trips_year
        ).annotate(
            avg_leader_score=Avg('scores__leader_score'),
            avg_croo_score=Avg('scores__croo_score')
        ).annotate(
            norm_avg_leader_score=Coalesce('avg_leader_score', V(0.0)),
            norm_avg_croo_score=Coalesce('avg_croo_score', V(0.0))
        )

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


class VolunteerQuerySet(models.QuerySet):

    def within_deadline_extension(self):
        """
        All applications that have a deadline extension and are within it.
        """
        return self.filter(
            deadline_extension__isnull=False,
            deadline_extension__gt=timezone.now())


VolunteerManager = BaseVolunteerManager.from_queryset(VolunteerQuerySet)


class QuestionManager(models.Manager):

    def required_for_leaders(self, trips_year):
        target_types = [self.model.LEADER, self.model.ALL]
        return self.required(trips_year).filter(type__in=target_types)

    def required_for_croos(self, trips_year):
        target_types = [self.model.CROO, self.model.ALL]
        return self.required(trips_year).filter(type__in=target_types)

    def required(self, trips_year):
        return self.filter(trips_year=trips_year, type__ne=self.model.OPTIONAL)


class GraderManager(models.Manager):

    def from_user(self, user):
        """Return the Grader object proxying the given user."""
        return self.get(pk=user.pk)

    # TODO: use subqueries in Django 1.11
    def for_year(self, trips_year):
        """
        Return all users who have scored applications this year.
        """
        qs = self.filter(scores__trips_year=trips_year).distinct()

        for user in qs:
            scores = user.scores.filter(trips_year=trips_year)
            user.score_count = scores.count()
            user.leader_score_avg = scores.aggregate(Avg('leader_score'))['leader_score__avg']
            user.croo_score_avg = scores.aggregate(Avg('croo_score'))['croo_score__avg']

            user.leader_score_histogram = histogram(scores, 'leader_score')
            user.croo_score_histogram = histogram(scores, 'croo_score')

        return qs


def SCORE_CHOICES():
    from .models import Score
    return Score.SCORE_CHOICES


def histogram(scores, field_name):
    """
    Create a histogram of the given scores, where histogram[1] is the
    number of `1`s granted, etc.
    """
    def box(x):
        return '{}{}'.format(field_name, x)

    histogram = scores.annotate(**dict(
        [box(x), OneIfTrue(**{field_name: x})]
        for x, _ in SCORE_CHOICES())
    ).aggregate(
        *(Sum(box(x)) for x, _ in SCORE_CHOICES())
    )

    return OrderedDict(
        (x, histogram[box(x) + '__sum'])
        for x, _ in SCORE_CHOICES()
    )


def OneIfTrue(**kwargs):
    return Case(
        When(then=1, **kwargs),
        default=0,
        output_field=models.IntegerField()
    )
