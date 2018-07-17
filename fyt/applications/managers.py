from collections import OrderedDict

from django.db import models
from django.db.models import (
    Q,
    Avg,
    Case,
    Count,
    Exists,
    FilteredRelation,
    Lookup,
    OuterRef,
    Prefetch,
    Sum,
    Value as V,
    When,
)
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

    def rejected(self, trips_year):
        return self.filter(trips_year=trips_year,
                           status=self.model.REJECTED)

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

    def with_avg_scores(self):
        """
        Annotate the queryset with average scores.

        Scores are coalesced into the normalized attribute so that, when
        ordering on Postgres, null values come after the actual scores.
        Note that this issue won't appear on a dev sqlite database.
        """
        return self.annotate(
            avg_leader_score=Avg('scores__leader_score__value'),
            avg_croo_score=Avg('scores__croo_score__value')
        ).annotate(
            norm_avg_leader_score=Coalesce('avg_leader_score', V(0.0)),
            norm_avg_croo_score=Coalesce('avg_croo_score', V(0.0))
        )

    def first_aid_complete(self):
        """
        All volunteers with complete first aid certifications.

        Complete certifications means a *verified* CPR certification, and
        a *verified* first aid certification, of some sort.
        """
        from fyt.training.models import FirstAidCertification

        CPR = FirstAidCertification.CPR
        non_cpr_options= [
            k for k, v in FirstAidCertification.CERTIFICATION_CHOICES
            if k not in (CPR, None)]

        return self.filter(
            first_aid_certifications__name=FirstAidCertification.CPR,
            first_aid_certifications__verified=True
        ).filter(
            first_aid_certifications__name__in=non_cpr_options,
            first_aid_certifications__verified=True
        )

    def first_aid_incomplete(self):
        """
        All volunteers missing first aid certifications.
        """
        return self.exclude(
            pk__in=self.model.objects.first_aid_complete().values_list('pk'))


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


class BaseGraderManager(models.Manager):

    def from_user(self, user):
        """Return the Grader object proxying the given user."""
        return self.get(pk=user.pk)


class GraderQuerySet(models.QuerySet):

    def with_statistics(self, trips_year):
        """
        Return all users who have scored applications this year.
        """
        LEADER_SCORE_LOOKUP = 'scores_for_year__leader_score'
        CROO_SCORE_LOOKUP = 'scores_for_year__croo_score'

        qs = self.annotate(
            scores_for_year=FilteredRelation('scores', condition=Q(
                scores__trips_year=trips_year))
        ).filter(
            scores_for_year__isnull=False
        ).distinct().annotate(
            score_count=Count('scores_for_year'),
            avg_leader_score=Avg(LEADER_SCORE_LOOKUP + '__value'),
            avg_croo_score=Avg(CROO_SCORE_LOOKUP + '__value')
        )

        qs = qs._annotate_score_counts(LEADER_SCORE_LOOKUP, trips_year)
        qs = qs._annotate_score_counts(CROO_SCORE_LOOKUP, trips_year)
        qs = qs._attach_histogram('leader_score_histogram', LEADER_SCORE_LOOKUP,
                                  trips_year)
        qs = qs._attach_histogram('croo_score_histogram', CROO_SCORE_LOOKUP,
                                  trips_year)

        return qs

    def _annotate_score_counts(self, score_lookup, trips_year):
        values = score_values(trips_year)
        return self.annotate(
            **{_bin(score_lookup, value): Count('scores_for_year', filter=Q(
                **{score_lookup: value}))
               for value in values})

    def _attach_histogram(self, histogram_name, score_lookup, trips_year):
        values = score_values(trips_year)
        for grader in self:
            setattr(grader, histogram_name, OrderedDict(
                (value, getattr(grader, _bin(score_lookup, value.value)))
                for value in values))
        return self


GraderManager = BaseGraderManager.from_queryset(GraderQuerySet)


def score_values(trips_year):
    from .models import ScoreValue
    return ScoreValue.objects.filter(trips_year=trips_year)


def _bin(score_lookup, x):
    return '{}_{}'.format(score_lookup, str(x).replace('.', '_'))


class ScoreQuerySet(models.QuerySet):

    def prefetch_display_data(self):
        from .models import ScoreComment
        return self.select_related(
            'grader',
            'leader_score',
            'croo_score'
        ).prefetch_related(
            Prefetch(
                'scorecomment_set',
                queryset=ScoreComment.objects.select_related(
                    'score_question')))


class ScoreClaimQuerySet(models.QuerySet):

    def active(self):
        """
        Filter claims that are currently active - that is, within the
        deadline and for which the user has not already scored or skipped
        the application.
        """
        from .models import Score, Skip

        return self.filter(
            claimed_at__gt=(timezone.now() - self.model.HOLD_DURATION)
        ).annotate(
            # Has the grader already added a score for this claim?
            already_scored=Exists(
                Score.objects.filter(
                    application=OuterRef('application'),
                    grader=OuterRef('grader')
                )
            ),
            # Has the grader already skipped this claim?
            already_skipped=Exists(
                Skip.objects.filter(
                    application=OuterRef('application'),
                    grader=OuterRef('grader')
                )
            )
        ).exclude(
            already_scored=True
        ).exclude(
            already_skipped=True
        )
