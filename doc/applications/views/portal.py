
from vanilla import TemplateView
from braces.views import LoginRequiredMixin

from doc.timetable.models import Timetable
from doc.db.models import TripsYear
from doc.applications.models import GeneralApplication


# TODO: Move this into templates? One template per choice?
# then each template can include trip information, etc.
# but will require more logic for figuring out what's available when.
STATUS_DESCRIPTIONS = {
    "PENDING": "Your application is still Pending. ",
    "CROO": "You've been accepted for a Croo!",
    "LEADER": "You're a Trip Leader! See below for information about your trip.",
    "LEADER_WAITLIST": "You're on the Leader Waitlist. People often back out of leading a Trip as the date gets nearer.", 
    "REJECTED": "Unfortunately, we had a lot of really strong applications this year. ",
    "CANCELLED": "Your application has been cancelled in the system. Please get in touch with the trip directors if you think this is an error.",
}


class VolunteerPortalView(LoginRequiredMixin, TemplateView):
    
    template_name = 'applications/portal.html'

    def get_context_data(self, **kwargs):
        
        context = super(VolunteerPortalView, self).get_context_data(**kwargs)
        context['timetable'] = Timetable.objects.timetable()
        context['trips_year'] = trips_year = TripsYear.objects.current()

        try:
            application = GeneralApplication.objects.get(
                trips_year=trips_year,
                applicant=self.request.user
            )
            application_status = STATUS_DESCRIPTIONS[application.status]

        except GeneralApplication.DoesNotExist:
            application = None
            application_status = "You did not submit an application"

        context['application'] = application
        context['status_description'] = application_status

        return context

    
