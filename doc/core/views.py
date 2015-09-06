from django.core.urlresolvers import reverse

from .models import Settings
from doc.db.views import DatabaseUpdateView
from doc.db.models import TripsYear


class EditSettings(DatabaseUpdateView):

    model = Settings
    template_name = 'form.html'
    delete_button = False

    def get_headline(self):
        return "Registration Settings"

    def get_trips_year(self):
        return TripsYear.objects.current().year

    def get_object(self):
        return Settings.objects.get(trips_year=self.get_trips_year())

    def get_success_url(self):
        return reverse('settings')
