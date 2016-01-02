
from vanilla import TemplateView, UpdateView
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy

from fyt.utils.forms import crispify
from fyt.timetable.models import Timetable
from fyt.db.models import TripsYear
from fyt.applications.models import GeneralApplication, PortalContent
from fyt.permissions.views import DatabaseEditPermissionRequired


class VolunteerPortalView(LoginRequiredMixin, TemplateView):

    template_name = 'applications/portal.html'

    def get_context_data(self, **kwargs):

        context = super(VolunteerPortalView, self).get_context_data(**kwargs)
        context['timetable'] = Timetable.objects.timetable()
        context['trips_year'] = trips_year = TripsYear.objects.current()
        context['content'] = content = PortalContent.objects.get(trips_year=trips_year)

        try:
            application = GeneralApplication.objects.get(
                trips_year=trips_year,
                applicant=self.request.user
            )
            status_description = content.get_status_description(application.status)
            context['is_trip_leader'] = (
                application.status == GeneralApplication.LEADER
            )
        except GeneralApplication.DoesNotExist:
            application = None
            status_description = "You did not submit an application"

        context['application'] = application
        context['status_description'] = status_description

        return context


class EditVolunteerPortalContent(DatabaseEditPermissionRequired, UpdateView):

    model = PortalContent
    fields = '__all__'
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


