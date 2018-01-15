from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from vanilla import TemplateView, UpdateView

from fyt.applications.models import PortalContent, Volunteer
from fyt.core.models import TripsYear
from fyt.permissions.views import SettingsPermissionRequired
from fyt.timetable.models import Timetable
from fyt.utils.forms import crispify


class VolunteerPortalView(LoginRequiredMixin, TemplateView):

    template_name = 'applications/portal.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        timetable = Timetable.objects.timetable()
        trips_year = TripsYear.objects.current()
        content = PortalContent.objects.get(trips_year=trips_year)

        context['trips_year'] = trips_year
        context['content'] = content
        context['applications_available'] = (
            timetable.applications_available)
        context['application_status_available'] = (
            timetable.application_status_available)
        context['applications_close'] = (
            timetable.applications_close)

        try:
            application = Volunteer.objects.get(
                trips_year=trips_year,
                applicant=self.request.user)

            status_description = content.get_status_description(
                application.status)
            context['show_trip_assignment'] = (
                timetable.leader_assignment_available and
                application.status == Volunteer.LEADER)
            context['show_trainings'] = (
                application.attendee.can_register)

        except Volunteer.DoesNotExist:
            application = None
            status_description = "You did not submit an application"

        context['application'] = application
        context['status_description'] = status_description

        return context


class EditVolunteerPortalContent(SettingsPermissionRequired, UpdateView):

    model = PortalContent
    fields = '__all__'
    template_name = 'applications/setup_portal.html'
    success_url = reverse_lazy('applications:setup_portal')

    def get_object(self):
        trips_year = TripsYear.objects.current()
        return self.model.objects.get(trips_year=trips_year)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        return crispify(form)
