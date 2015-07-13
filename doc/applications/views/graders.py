
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg
from vanilla import ListView

from doc.db.views import TripsYearMixin
from doc.permissions.views import DatabaseReadPermissionRequired

DartmouthUser = get_user_model()


def get_graders(trips_year):
    """
    Return all Users who have graded applications this year.
    
    Returns both croo and leader graders. Attachs an 'avg_leader_grade'
    and 'avg_croo_grade' to each grader. Unfortunately that computation 
    can't be done with an .annotate call on the users queryset since the
    grades have to be restricted to this trips_year; a user could have
    graded the year before and we don't want to confuse their averages.
    """
    users = (
        DartmouthUser.objects.filter(
            Q(leaderapplicationgrades__trips_year=trips_year) |
            Q(crooapplicationgrades__trips_year=trips_year))
        .distinct())

    for user in users:
        leader_grades = user.leaderapplicationgrades.filter(trips_year=trips_year)
        user.avg_leader_grade = leader_grades.aggregate(Avg('grade'))['grade__avg']
        user.leader_grade_count = leader_grades.count()

        croo_grades = user.crooapplicationgrades.filter(trips_year=trips_year)
        user.avg_croo_grade = croo_grades.aggregate(Avg('grade'))['grade__avg']
        user.croo_grade_count = croo_grades.count()

    return users


class GraderList(DatabaseReadPermissionRequired, TripsYearMixin, ListView):
    """ 
    List view of all graders for this trips year
    
    Shows name, average score, # of applications scored for both
    Trip Leader and Croo applications.
    """

    template_name = 'applications/grader_list.html'
    context_object_name = 'graders'

    def get_queryset(self):
        return get_graders(self.kwargs['trips_year'])
