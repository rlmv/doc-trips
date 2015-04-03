
from vanilla import TemplateView, UpdateView
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy

from doc.utils.forms import crispify
from doc.timetable.models import Timetable
from doc.db.models import TripsYear
from doc.applications.models import GeneralApplication, PortalContent
from doc.permissions.views import DatabaseEditPermissionRequired


# TODO: Move this into templates? One template per choice?
# then each template can include trip information, etc.
# but will require more logic for figuring out what's available when.
STATUS_DESCRIPTIONS = {
    GeneralApplication.PENDING: "Your application is still Pending.",
    GeneralApplication.CROO: "You've been accepted for a Croo!",
    GeneralApplication.LEADER: "You're a Trip Leader!",
    GeneralApplication.LEADER_WAITLIST: "You're on the Leader Waitlist. People often back out of leading a Trip as the date gets nearer.", 
    GeneralApplication.REJECTED: "Unfortunately, we had a lot of really strong applications this year. ",
    GeneralApplication.CANCELED: "Your application has been cancelled in the system. Please get in touch with the trip directors if you think this is an error.",
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
            status_description = STATUS_DESCRIPTIONS[application.status]
            context['is_trip_leader'] = (
                application.status == GeneralApplication.LEADER
            )
            context['is_croo'] = (
                application.status == GeneralApplication.CROO
            )
        except GeneralApplication.DoesNotExist:
            application = None
            status_description = "You did not submit an application"

        context['application'] = application
        context['status_description'] = status_description

        return context


class EditVolunteerPortalContent(DatabaseEditPermissionRequired, UpdateView):

    model = PortalContent
    template_name = 'applications/setup_portal.html'
    success_url = reverse_lazy('applications:setup_portal')
    
    def get_object(self):
        trips_year = TripsYear.objects.current()
        # changing state in a GET is not semantically correct, but hey...
        obj, ctd = self.model.objects.get_or_create(trips_year=trips_year)
        return obj

    def get_form(self, *args, **kwargs):
        form = super(EditVolunteerPortalContent, self).get_form(*args, **kwargs)
        return crispify(form)

    
