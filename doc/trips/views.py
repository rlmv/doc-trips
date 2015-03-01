
from collections import defaultdict

from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from bootstrap3_datetime.widgets import DateTimePicker

from doc.trips.models import ScheduledTrip, TripTemplate, TripType, Campsite, Section
from doc.db.views import (DatabaseCreateView, DatabaseUpdateView, DatabaseDeleteView,
                      DatabaseListView, DatabaseDetailView)


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
    fields = ['section', 'template']

class ScheduledTripDetailView(DatabaseDetailView):
    model = ScheduledTrip

class ScheduledTripCreateView(DatabaseCreateView):
    model = ScheduledTrip
    fields = ['section', 'template']

    def get_form(self, data=None, files=None, **kwargs):
        """ Populate the CreateForm with query parameters

        Used by the trip_index.html template to link to a create form 
        for a template-section pair

        TODO: make the form fields uneditable.
        """

        cls = self.get_form_class()

        GET = self.request.GET
        if data is None and 'section' in GET and 'template' in GET:
            data = {'section': GET['section'], 'template': GET['template']}
        
        return super(ScheduledTripCreateView, self).get_form(data=data, files=files, **kwargs)
        

class ScheduledTripDeleteView(DatabaseDeleteView):
    model = ScheduledTrip
    success_url_pattern = 'db:scheduledtrip_index'


class TripTemplateListView(DatabaseListView):
    model = TripTemplate
    context_object_name = 'templates' 
    template_name = 'trip/template_index.html'

class TripTemplateCreateView(DatabaseCreateView):
    model = TripTemplate

class TripTemplateDetailView(DatabaseDetailView):
    model = TripTemplate
    fields = ['name', 'description_summary', 'triptype', 
              'max_trippees', 'non_swimmers_allowed', 'dropoff', 
              'campsite1', 'campsite2', 'pickup', 'return_route',
              'description_introduction', 'description_day1', 
              'description_day2', 'description_day3', 
              'description_conclusion', 'revision_notes']
              

class TripTemplateUpdateView(DatabaseUpdateView):
    model = TripTemplate

class TripTemplateDeleteView(DatabaseDeleteView):
    model = TripTemplate
    success_url_pattern = 'db:template_index'
    

class TripTypeListView(DatabaseListView):
    model = TripType
    context_object_name = '{}s'.format(TripType.get_model_name_lower())
    template_name = 'trip/triptype_index.html'

class TripTypeCreateView(DatabaseCreateView):
    model = TripType

class TripTypeDetailView(DatabaseDetailView):
    model = TripType
    fields = ['name', 'trippee_description', 'leader_description', 
              'packing_list']

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
        context = super(CampsiteListView, self).get_context_data(**kwargs)
        context['camping_dates'] = Section.dates.camping_dates(trips_year)
        return context

class CampsiteCreateView(DatabaseCreateView):
    model = Campsite

class CampsiteDetailView(DatabaseDetailView):
    model = Campsite
    fields = ['name', 'capacity', 'directions', 'bugout', 'secret']

class CampsiteUpdateView(DatabaseUpdateView):
    model = Campsite

class CampsiteDeleteView(DatabaseDeleteView):
    model = Campsite
    success_url_pattern = 'db:campsite_index'


class SectionListView(DatabaseListView):
    model = Section
    context_object_name = 'sections'
    template_name = 'trip/section_index.html'

class SectionForm(ModelForm):
    """ Form for Section Create and Update views. """
    
    class Meta:
        model = Section
        widgets = {
            'leaders_arrive': DateTimePicker(options={'format': 'MM/DD/YYYY', 
                                                      'pickTime': False})
        }

    def __init__(self, *args, **kwargs):
        super(SectionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))
    

class SectionCreateView(DatabaseCreateView):
    model = Section
    form_class = SectionForm
    template_name = 'trip/section_create.html'

class SectionDetailView(DatabaseDetailView):
    model = Section
    fields = ['name', 'leaders_arrive', 'is_local', 'is_exchange', 
              'is_transfer', 'is_international', 'is_native', 'is_fysep']

class SectionUpdateView(DatabaseUpdateView):
    model = Section
    form_class = SectionForm
    template_name = 'trip/section_update.html'

class SectionDeleteView(DatabaseDeleteView):
    model = Section
    success_url_pattern = 'db:section_index'
                               

class TripLeaderIndexView(DatabaseListView):
    """ Show all ScheduledTrips and assigned leaders + links to assign leaders """
    model = ScheduledTrip
    template_name = 'trip/leaders.html'
    
    def get_queryset(self):
        qs = super(TripLeaderIndexView, self).get_queryset()
        return qs.order_by('section', 'template')

    def get_context_data(self, **kwargs):

        context = super(TripLeaderIndexView, self).get_context_data(**kwargs)
        context['sections'] = Section.objects.filter(trips_year=self.kwargs['trips_year'])

        trips_by_section = defaultdict(list)
        for trip in self.object_list:
            trips_by_section[trip.section].append(trip)
        # value lists in trips_by_section will by sorted by trip #
        # give a tuple (section, [trips]) to the template
        context['trips_by_section'] = list(trips_by_section.items())
        
        return context
        
        
    
