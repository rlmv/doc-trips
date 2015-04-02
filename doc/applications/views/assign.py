from vanilla import UpdateView

from doc.utils.forms import crispify
from doc.permissions.views import ApplicationEditPermissionRequired
from doc.db.views import TripsYearMixin
from doc.applications.models import GeneralApplication


class AssignToTrip(ApplicationEditPermissionRequired, TripsYearMixin,
                   UpdateView):
    """
    Assign LEADER to a ScheduledTrip.

    Shows availability, preferences
    """

    model = GeneralApplication
    template_name = 'db/update.html'
    fields = ['assigned_trip']

    def get_form(self, **kwargs):
        form = super(AssignToTrip, self).get_form(**kwargs)
        return crispify(form, submit_text='Update Assignment')
