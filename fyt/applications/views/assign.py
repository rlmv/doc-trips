from vanilla import UpdateView

from ..forms import TripAssignmentForm
from ..models import Volunteer
from ..views.application import BlockOldApplications

from fyt.core.views import TripsYearMixin
from fyt.permissions.views import ApplicationEditPermissionRequired
from fyt.utils.forms import crispify
from fyt.utils.views import ExtraContextMixin


class AssignToTrip(ApplicationEditPermissionRequired, BlockOldApplications,
                   TripsYearMixin, ExtraContextMixin, UpdateView):
    """
    Assign LEADER to a Trip.

    Shows availability, preferences
    """
    model = Volunteer
    template_name = 'applications/trip_assignment_update.html'
    form_class = TripAssignmentForm

    def extra_context(self):
        order = lambda qs: qs.order_by(
            'template__triptype',
            'section',
            'template'
        )
        return {
            'preferred_trips': order(self.object.get_preferred_trips()),
            'available_trips': order(self.object.get_available_trips())
        }


class AssignToCroo(ApplicationEditPermissionRequired, BlockOldApplications,
                   TripsYearMixin, UpdateView):
    """
    Assign volunteer to a croo
    """
    model = Volunteer
    template_name = 'core/update.html'
    fields = ['assigned_croo']

    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)
        return crispify(form)
