
from collections import defaultdict

from django.core.urlresolvers import reverse_lazy, reverse
from vanilla import FormView
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from braces.views import FormValidMessageMixin

from doc.trips.models import ScheduledTrip, TripTemplate, TripType, Campsite, Section
from doc.trips.forms import TripLeaderAssignmentForm, SectionForm
from doc.applications.models import LeaderSupplement
from doc.db.views import (DatabaseCreateView, DatabaseUpdateView, DatabaseDeleteView,
                          DatabaseListView, DatabaseDetailView, DatabaseMixin)
from doc.db.urlhelpers import reverse_detail_url


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
        
    
class AssignTripLeaderView(DatabaseListView):
    """ 
    Assign a leader to a ScheduledTrip. 

    Takes the trip pk as a url arg. The template is passed 
    a list of (LeaderApplication, assignment_form, triptype_preference, section_pref) 
    tuples in context_object_name. assignment_form will be None if the leader 
    is already assigned to a trip.
    """

    model = LeaderSupplement
    template_name = 'trip/assign_leader.html'
    context_object_name = 'leader_applications'

    def get_queryset(self):
        trip = ScheduledTrip.objects.get(pk=self.kwargs['trip'])
        return self.model.objects.prospective_leaders_for_trip(trip)

    def get_context_data(self, **kwargs):
        context = super(AssignTripLeaderView, self).get_context_data(**kwargs)

        trip = ScheduledTrip.objects.get(pk=self.kwargs['trip'])
        context['trip'] = trip

        def process_leader(leader):

            if leader.assigned_trip:
                form = None
            else:
                form = TripLeaderAssignmentForm(initial={'assigned_trip': trip}, 
                                                instance=leader)
                
            if trip.template.triptype in leader.preferred_triptypes.all():
                triptype_preferrence = 'prefer'
            elif trip.template.triptype in leader.available_triptypes.all():
                triptype_preferrence = 'available'

            if trip.section in leader.preferred_sections.all():
                section_preferrence = 'prefer'
            elif trip.section in leader.available_sections.all():
                section_preferrence = 'available'
                
            return (leader, form, triptype_preferrence, section_preferrence)
        
        # prefetch M2M fields
        leaders = (self.object_list
                   .prefetch_related('preferred_triptypes')
                   .prefetch_related('available_triptypes')
                   .prefetch_related('preferred_sections')
                   .prefetch_related('available_sections'))
        context[self.context_object_name] = map(process_leader, leaders)
        
        return context


class UpdateLeaderWithAssignedTrip(FormValidMessageMixin, DatabaseUpdateView):
    """ 
    Add an assigned_trip to a leader. 

    POST target for AssignTripLeaderView 
    """
    model = LeaderSupplement
    form_class = TripLeaderAssignmentForm
    lookup_url_kwarg = 'leader_pk'

    def get_form_valid_message(self):
        """ Flash success message """
        return '{} assigned to lead {}'.format(self.object.application.applicant, 
                                               self.object.assigned_trip)

    def get_success_url(self):
        """ Override DatabaseUpdateView default """
        return reverse('db:leader_index', 
                       kwargs={'trips_year': self.kwargs['trips_year']})


class RemoveAssignedTrip(FormValidMessageMixin, DatabaseUpdateView):
    """ Remove a leader's assigned trip """

    model = LeaderSupplement
    lookup_url_kwarg = 'leader_pk'
    template_name = 'trip/remove_leader_assignment.html'

    def get_form(self, **kwargs):

        # save the old assigned trip so we can show it in a message after deletion
        self._assigned_trip = kwargs['instance'].assigned_trip

        form = TripLeaderAssignmentForm(initial={'assigned_trip': None}, **kwargs)
        
        form.helper = FormHelper(form)
        form.helper.add_input(Submit('submit', 'Remove', css_class="btn-danger"))
        return form

    def get_form_valid_message(self):
        return 'Leader {} removed from Trip {}'.format(self.object.application.applicant,
                                                       self._assigned_trip)
        
    def get_success_url(self):
        return reverse_detail_url(self.object.application)
        
        
    
    
    
    
        
