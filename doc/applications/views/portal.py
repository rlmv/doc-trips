
from vanilla import TemplateView
from braces.views import LoginRequiredMixin

from doc.timetable.models import Timetable
from doc.db.models import TripsYear
from doc.applications.models import GeneralApplication


STATUS_DESCRIPTIONS = {
    "PENDING": "",
    "CROO": "",
    "LEADER": "",
    "LEADER_WAITLIST": "", 
    "REJECTED": "",
    "CANCELLED": "",
}


class VolunteerPortalView(LoginRequiredMixin, TemplateView):
    
    template_name = 'applications/portal.html'

    def get_context_data(self, **kwargs):
        
        context = super(VolunteerPortalView, self).get_context_data(**kwargs)
        context['timetable'] = Timetable.objects.timetable()

        try:
            application = GeneralApplication.objects.get(
                trips_year=TripsYear.objects.current(),
                applicant=self.request.user
            )
        except GeneralApplication.DoesNotExist:
            application = None

        context['application'] = application
        context['status'] = application.get_status_display()
        context['status_description'] = STATUS_DESCRIPTIONS[application.status]

        return context

    
