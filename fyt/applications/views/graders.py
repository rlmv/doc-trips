from vanilla import ListView

from fyt.applications.models import Grader, Score, ScoreValue, Volunteer
from fyt.core.views import TripsYearMixin
from fyt.permissions.views import GraderTablePermissionRequired
from fyt.utils.views import ExtraContextMixin


class GraderList(
    GraderTablePermissionRequired, ExtraContextMixin, TripsYearMixin, ListView
):
    """
    List view of all graders for this trips year

    Shows name, average score, # of applications scored for both
    Trip Leader and Croo applications.
    """

    template_name = 'applications/grader_list.html'
    context_object_name = 'graders'

    def get_queryset(self):
        return Grader.objects.with_statistics(self.trips_year)

    def extra_context(self):
        return {
            'score_values': ScoreValue.objects.filter(trips_year=self.trips_year),
            'progress': Volunteer.objects.score_progress(self.trips_year),
        }
