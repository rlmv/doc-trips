
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg
from vanilla import ListView

from doc.db.views import TripsYearMixin
from doc.permissions.views import DatabaseReadPermissionRequired

DartmouthUser = get_user_model()


def get_graders(trips_year):
    """ 
    Return all Users who have graded applications this year.
    
    Does not distinguish between croo and leader applications.
    """

    return (DartmouthUser.objects
            .filter(Q(leaderapplicationgrades__trips_year=trips_year) |
                    Q(crooapplicationgrades__trips_year=trips_year))
        )


class GraderListView(DatabaseReadPermissionRequired, TripsYearMixin,
                     ListView):
    """ 
    List view of all graders for this trips year
    
    Shows name, average score, # of applications scored for both
    Trip Leader and Croo applications.
    """

    template_name = 'applications/grader_list.html'
    context_object_name = 'graders'

    def get_queryset(self):
        return get_graders(self.kwargs['trips_year'])

                    
                
                
