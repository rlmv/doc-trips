
from collections import defaultdict

from django import forms
from django.forms import ModelForm
from django.core.urlresolvers import reverse_lazy, reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from bootstrap3_datetime.widgets import DateTimePicker
from vanilla import FormView

from doc.trips.models import ScheduledTrip, TripTemplate, TripType, Campsite, Section
from doc.applications.models import LeaderSupplement
from doc.db.views import (DatabaseCreateView, DatabaseUpdateView, DatabaseDeleteView,
                          DatabaseListView, DatabaseDetailView, DatabaseMixin)


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

        trips_by_section = defaultdict(list)
        for trip in self.object_list:
            trips_by_section[trip.section].append(trip)
        # value lists in trips_by_section will by sorted by trip #
        # give a tuple (section, [trips]) to the template
        context['trips_by_section'] = list(trips_by_section.items())
        
        return context
        

class TripLeaderAssignmentForm(forms.ModelForm):
    
    class Meta:
        model = LeaderSupplement
        fields = ['assigned_trip']
        widgets = {
            'assigned_trip': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(TripLeaderAssignmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse('db:assign_trip_to_leader', 
                                          kwargs={'trips_year': kwargs['instance'].trips_year.year,
                                                  'leader_pk': kwargs['instance'].pk})
        self.helper.add_input(Submit('submit', 'Add'))

    
class AssignTripLeaderView(DatabaseListView):
    """ 
    Assign a leader to a ScheduledTrip. 

    Takes the trip pk as a url arg. The template is passed 
    a (LeaderApplication, assignment_form tuple in context_object_name.
    """
    model = LeaderSupplement
    template_name = 'trip/assign_leader.html'
    context_object_name = 'leader_applications'

    def get_context_data(self, **kwargs):
        context = super(AssignTripLeaderView, self).get_context_data(**kwargs)
        # add forms to each object 
        context['trip'] = ScheduledTrip.objects.get(pk=self.kwargs['trip'])
        context[self.context_object_name] = self.get_forms_for_leaders(self.object_list, 
                                                                       self.kwargs['trip'])
        return context

    def get_forms_for_leaders(self, leaders, trip):

        def assign_form(leader):
            form = TripLeaderAssignmentForm(initial={'assigned_trip': trip}, 
                                            instance=leader)
            return (leader, form)

        return map(leaders, assign_form)
        
        
class UpdateLeaderWithAssignedTrip(DatabaseUpdateView):
    """ 
    Add an assigned_trip to a leader. 

    POST target for AssignTripLeaderView 
    """
    model = LeaderSupplement
    form_class = TripLeaderAssignmentForm
    success_url = reverse_lazy('db:leader_index')
    lookup_url_kwarg = 'leader_pk'
        
