

from db.views import (DatabaseCreateView, DatabaseUpdateView, DatabaseDeleteView,
                      DatabaseListView, DatabaseDetailView)

from transport.models import Stop, Route, Vehicle


class StopListView(DatabaseListView):
    model = Stop
    context_object_name = 'stops'
    template_name = 'transport/stop_index.html'

class StopCreateView(DatabaseCreateView):
    model = Stop

class StopDetailView(DatabaseDetailView):
    model = Stop

class StopUpdateView(DatabaseUpdateView):
    model = Stop

class StopDeleteView(DatabaseDeleteView):
    model = Stop
    success_url_pattern = 'db:stop_index'
