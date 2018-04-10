from vanilla import ListView

from fyt.applications.models import Grader, Score, Volunteer
from fyt.core.views import TripsYearMixin
from fyt.permissions.views import GraderTablePermissionRequired
from fyt.utils.views import ExtraContextMixin


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
        return Grader.objects.for_year(self.get_trips_year())

    def extra_context(self):
        return {
            'score_choices': [x for x, _ in Score.SCORE_CHOICES],
            'progress': Volunteer.objects.score_progress(
                self.get_trips_year())
        }
