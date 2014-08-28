
from trip.models import ScheduledTrip, TripTemplate, TripType, Campsite, Section
from db.views import (DatabaseCreateView, DatabaseUpdateView, DatabaseDeleteView,
                     DatabaseListView, DatabaseViewFactory)


class ScheduledTripListView(DatabaseListView):
    model = ScheduledTrip
    template_name = 'trip/trip_index.html'
    context_object_name = 'trips'

class ScheduledTripUpdateView(DatabaseUpdateView):
    model = ScheduledTrip
    success_url_pattern = 'db:trip:trip_update'

class ScheduledTripCreateView(DatabaseCreateView):
    model = ScheduledTrip
    success_url_pattern = 'db:trip:trip_update'

class ScheduledTripDeleteView(DatabaseDeleteView):
    model = ScheduledTrip
    template_name = 'db/update.html'
    success_url_pattern = 'db:trip:trip_index'


class TripTemplateListView(DatabaseListView):
    model = TripTemplate
    template_name = 'trip/template_index.html'
    context_object_name = 'templates' 

class TripTemplateCreateView(DatabaseCreateView):
    model = TripTemplate

class TripTemplateUpdateView(DatabaseUpdateView):
    model = TripTemplate

class TripTemplateDeleteView(DatabaseDeleteView):
    model = TripTemplate
    success_url_pattern = 'db:template:template_index'
    
TripTypeViews = DatabaseViewFactory(TripType)

CampsiteViews = DatabaseViewFactory(Campsite)

SectionViews = DatabaseViewFactory(Section)
                               
