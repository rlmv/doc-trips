from django.urls import reverse

from .models import Gear, GearRequest

from fyt.core.views import (
    DatabaseCreateView,
    DatabaseListView,
    DatabaseUpdateView,
)


class GearList(DatabaseListView):
    model = Gear


class GearCreate(DatabaseCreateView):
    model = Gear

    def get_headline(self):
        return "Add a new piece of gear"

    def get_success_url(self):
        return reverse('core:gear:list', kwargs=self.kwargs)


class GearUpdate(DatabaseUpdateView):
    model = Gear
    delete_button = False

    def get_success_url(self):
        return reverse('core:gear:list', kwargs={'trips_year': self.trips_year})
