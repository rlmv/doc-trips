
from collections import OrderedDict

from django.db import models
from django.db.models import Q, Avg, Case, Count, Sum, When
from vanilla import ListView

from fyt.applications.models import Score, Volunteer
from fyt.db.views import TripsYearMixin
from fyt.permissions.views import GraderTablePermissionRequired
from fyt.users.models import DartmouthUser
from fyt.utils.views import ExtraContextMixin


def users_with_old_grades(trips_year):
    return DartmouthUser.objects.filter(
        Q(leaderapplicationgrades__trips_year=trips_year) |
        Q(crooapplicationgrades__trips_year=trips_year)
    ).distinct()


def _old_get_graders(trips_year):
    """
    Deprecated when scoring changed to use a single Score object.

    Return all Users who have graded applications this year.

    Returns both croo and leader graders. Attachs an 'avg_leader_grade'
    and 'avg_croo_grade' to each grader. Unfortunately that computation
    can't be done with an .annotate call on the users queryset since the
    grades have to be restricted to this trips_year; a user could have
    graded the year before and we don't want to confuse their averages.
    """
    users = users_with_old_grades(trips_year)

    for user in users:
        leader_grades = user.leaderapplicationgrades.filter(trips_year=trips_year)
        user.avg_leader_grade = leader_grades.aggregate(Avg('grade'))['grade__avg']
        user.leader_grade_count = leader_grades.count()

        croo_grades = user.crooapplicationgrades.filter(trips_year=trips_year)
        user.avg_croo_grade = croo_grades.aggregate(Avg('grade'))['grade__avg']
        user.croo_grade_count = croo_grades.count()

    return users


# TODO: use subqueries in Django 1.11
def get_graders(trips_year):
    """
    Return all users who have scored applications this year.
    """
    qs = DartmouthUser.objects.filter(scores__trips_year=trips_year).distinct()

    for user in qs:
        scores = user.scores.filter(trips_year=trips_year)
        user.score_count = scores.count()
        user.score_avg = scores.aggregate(Avg('score'))['score__avg']

        # Attach a histogram of scores for each user
        # score_histogram[1] is the number of `1`s granted, etc.
        def box(x):
            return 'score{}'.format(x)

        histogram = scores.annotate(**dict(
            [box(x), OneIfTrue(score=x)]
            for x, _ in Score.SCORE_CHOICES)
        ).aggregate(
            *(Sum(box(x)) for x, _ in Score.SCORE_CHOICES)
        )

        user.score_histogram = OrderedDict(
            (x, histogram[box(x) + '__sum'])
            for x, _ in Score.SCORE_CHOICES
        )

    return qs


def OneIfTrue(**kwargs):
    return Case(
        When(then=1, **kwargs),
        default=0,
        output_field=models.IntegerField()
    )


class GraderList(GraderTablePermissionRequired, ExtraContextMixin,
                 TripsYearMixin, ListView):
    """
    List view of all graders for this trips year

    Shows name, average score, # of applications scored for both
    Trip Leader and Croo applications.
    """

    template_name = 'applications/grader_list.html'
    context_object_name = 'graders'

    def get_queryset(self):
        trips_year = self.get_trips_year()

        if users_with_old_grades(trips_year).exists():
            assert not get_graders(trips_year).exists()
            return _old_get_graders(trips_year)

        return get_graders(trips_year)

    def extra_context(self):
        return {
            'show_old_grades': users_with_old_grades(
                self.get_trips_year()).exists(),
            'score_choices': [x for x, _ in Score.SCORE_CHOICES],
            'progress': Volunteer.objects.score_progress(
                self.get_trips_year())
        }
