
from trip.models import ScheduledTrip, TripTemplate, TripType, Campsite, Section
from db.views import (DatabaseCreateView, DatabaseUpdateView, DatabaseDeleteView,
                     DatabaseListView, DatabaseViewFactory)


class ScheduledTripListView(DatabaseListView):
    """ Note: this queries on TripTemplates, not ScheduledTrips 
    Rename to clarify?
    """
    model = TripTemplate
    template_name = 'trip/trip_index.html'
    context_object_name = 'templates'

    def get_context_data(self, **kwargs):
        """ Add sections to template context """
        context = super(ScheduledTripListView, self).get_context_data(**kwargs)
        trips_year = self.kwargs['trips_year']
        # TODO: optimize this using .only? vv
        context['sections'] = Section.objects.filter(trips_year=trips_year)
        return context

class ScheduledTripUpdateView(DatabaseUpdateView):
    model = ScheduledTrip
    success_url_pattern = 'db:trip:trip_update'

class ScheduledTripCreateView(DatabaseCreateView):
    model = ScheduledTrip
    success_url_pattern = 'db:trip:trip_update'

    def get_form(self, data=None, files=None, **kwargs):
        """ Populate the CreateForm with query parameters

        Used by the trip_index.html template to link to a create form 
        for a template-section pair

        TODO: should this be simplified to 
        if GET has items:
           data = GET
        ??
        """

        cls = self.get_form_class()
        
        GET = self.request.GET
        if 'section' in GET and 'template' in GET:
            data = {'section': GET['section'], 'template': GET['template']}
        
        return cls(data=data, files=files, **kwargs)
        

class ScheduledTripDeleteView(DatabaseDeleteView):
    model = ScheduledTrip
    success_url_pattern = 'db:trip:trip_index'


class TripTemplateListView(DatabaseListView):
    model = TripTemplate
    context_object_name = 'templates' 
    template_name = 'trip/template_index.html'

class TripTemplateCreateView(DatabaseCreateView):
    model = TripTemplate

class TripTemplateUpdateView(DatabaseUpdateView):
    model = TripTemplate

class TripTemplateDeleteView(DatabaseDeleteView):
    model = TripTemplate
    success_url_pattern = 'db:template_index'
    

class TripTypeListView(DatabaseListView):
    model = TripType
    context_object_name = '{}s'.format(TripType.get_reference_name())
    template_name = 'trip/triptype_index.html'

class TripTypeCreateView(DatabaseCreateView):
    model = TripType

class TripTypeUpdateView(DatabaseUpdateView):
    model = TripType

class TripTypeDeleteView(DatabaseDeleteView):
    model = TripType
    success_url_pattern = 'db:triptype_index'


class CampsiteListView(DatabaseListView):
    model = Campsite
    context_object_name = 'campsites'
    template_name = 'trip/campsite_index.html'
    
    def get_context_data(self, **kwargs):
        trips_year = self.kwargs['trips_year']
        context = super(CampsiteViews.IndexView, self).get_context_data(**kwargs)
        context['camping_dates'] = Section.dates.camping_dates(trips_year)
        return context

class CampsiteCreateView(DatabaseCreateView):
    model = Campsite

class CampsiteUpdateView(DatabaseUpdateView):
    model = Campsite

class CampsiteDeleteView(DatabaseDeleteView):
    model = Campsite
    success_url_pattern = 'db:campsite_index'


class SectionListView(DatabaseListView):
    model = Section
    context_object_name = 'sections'
    template_name = 'trip/section_index.html'

class SectionCreateView(DatabaseCreateView):
    model = Section

class SectionUpdateView(DatabaseUpdateView):
    model = Section

class SectionDeleteView(DatabaseDeleteView):
    model = Section
    success_url_pattern = 'db:section_index'
                               
