from vanilla import UpdateView
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

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
        form.helper = FormHelper(form)
        form.helper.add_input(Submit('submit', 'Update Assignment'))
        return form
   
