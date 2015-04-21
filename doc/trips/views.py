from statistics import mean
from collections import defaultdict

from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Avg
from vanilla import FormView, UpdateView
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from braces.views import FormValidMessageMixin, SetHeadlineMixin

from doc.trips.models import ScheduledTrip, TripTemplate, TripType, Campsite, Section
from doc.trips.forms import TripLeaderAssignmentForm, SectionForm, AssignmentForm
from doc.applications.models import LeaderSupplement, GeneralApplication
from doc.db.views import (DatabaseCreateView, DatabaseUpdateView, DatabaseDeleteView,
                          DatabaseListView, DatabaseDetailView, 
                          TripsYearMixin)
from doc.permissions.views import ApplicationEditPermissionRequired
from doc.db.urlhelpers import reverse_detail_url
from doc.utils.forms import crispify


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
    template_name = 'trip/trip_detail.html'

    fields = ['section', 'template', 'leaders', 'trippees']

    triptemplate_fields = [
        'triptype', 'max_trippees', 'non_swimmers_allowed', 
        'description_introduction', 
        'dropoff', 'description_day1', 'campsite1',
        'description_day2', 'campsite2',
        'description_day3', 'pickup',
        'description_conclusion', 
        'return_route', 
        'revision_notes']
    

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
    
    def get_queryset(self):
        qs = super(TripTemplateListView, self).get_queryset()
        return qs.select_related(
            'triptype', 'campsite1', 'campsite2', 'dropoff', 'pickup'
        )


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
    success_url_pattern = 'db:triptemplate_index'
    

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
    context_object_name = 'trips'
    
    def get_queryset(self):
        return (
            super(TripLeaderIndexView, self).get_queryset()
            .select_related('section', 'template')
            .prefetch_related('leaders', 'leaders__applicant')
            .order_by('section', 'template')
        )

       
class AssignTripLeaderView(DatabaseListView):
    """ 
    Assign a leader to a ScheduledTrip. 

    Takes the trip pk as a url arg. The template is passed 
    a list of (LeaderApplication, assignment_form, triptype_preference, section_pref) 
    tuples in context_object_name. assignment_form will be None if the leader 
    is already assigned to a trip.
    """

    model = GeneralApplication
    template_name = 'trip/assign_leader.html'
    context_object_name = 'leader_applications'

    def get_trip(self):
        if not hasattr(self, 'trip'):
            self.trip = ScheduledTrip.objects.get(pk=self.kwargs['trip'])
        return self.trip

    def get_queryset(self):
        qs = (
            self.model.objects.prospective_leaders_for_trip(self.get_trip())
            .select_related('applicant')
            .select_related('assigned_trip', 'assigned_trip__template')
            .select_related('assigned_trip__section')
#            .prefetch_related('leader_supplement__preferred_triptypes')
#            .prefetch_related('leader_supplement__available_triptypes')
#            .prefetch_related('leader_supplement__preferred_sections')
#            .prefetch_related('leader_supplement__available_sections')
            .prefetch_related('leader_supplement__grades')
            .only('trips_year', 'gender',
                  'applicant__name',
                  'assigned_trip__trips_year_id',
                  'assigned_trip__template__name',
                  'assigned_trip__section__name',
                  'status')
        )

        # fix issue with aggregation.
        # For some reason, annotating grades using Avg adds an 
        # expensive GROUP BY clause to the query, killing the site.
        # See https://code.djangoproject.com/ticket/17144. 
        # Does this need to be reopened?
        # TODO: check with 1.8
        # This is a hackish workaround to explicitly compute the
        # average for all applications with reasonable performance:
        for app in qs:
            app.avg_grade = mean(
                map(lambda g: g.grade, app.leader_supplement.grades.all())
            )
        return sorted(qs, key=lambda x: x.avg_grade, reverse=True)

    def get_context_data(self, **kwargs):
        context = super(AssignTripLeaderView, self).get_context_data(**kwargs)
        context['trip'] = trip = self.get_trip()

        def process_leader(leader):

            if leader.assigned_trip:
                link = None
            else:
                link = reverse('db:assignment', kwargs={'trips_year': leader.trips_year_id, 'leader_pk': leader.pk}) + '?assign_to=%s' % trip.pk
               
            # See http://stackoverflow.com/questions/10273744/django-many-to-many-field-prefetch-primary-keys-only
            """
            if trip.template.triptype in ls.preferred_triptypes.all():
                triptype_preferrence = 'prefer'
            elif trip.template.triptype in ls.available_triptypes.all():
                triptype_preferrence = 'available'

            if trip.section in ls.preferred_sections.all():
                section_preferrence = 'prefer'
            elif trip.section in ls.available_sections.all():
                section_preferrence = 'available'
            """
            triptype_preferrence = "--"
            section_preferrence = "--"
                
            return (leader, link, triptype_preferrence, section_preferrence)

        context[self.context_object_name] = map(process_leader, self.object_list)
        return context

# should these volunteer specific views go to the applications app?

class AssignLeaderToTrip(ApplicationEditPermissionRequired, 
                         FormValidMessageMixin, SetHeadlineMixin, TripsYearMixin, 
                         UpdateView):

    model = GeneralApplication
    lookup_url_kwarg = 'leader_pk'
    template_name = 'db/update.html'
    form_class = AssignmentForm

    def get(self, request, *args, **kwargs):
        
        data = None
        GET = request.GET
        if 'assign_to' in GET:
            data = {'assigned_trip': GET['assign_to']}
        form = self.get_form(data=data)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_form(self, **kwargs):
        return self.get_form_class()(self.kwargs['trips_year'], **kwargs)
    
    def get_form_valid_message(self):
        """ Flash success message """
        return '{} assigned to lead {}'.format(
            self.object.applicant, self.object.assigned_trip
        )

    def get_headline(self):
        self.object = self.get_object()
        return 'Assign {} to trip'.format(
            self.object.applicant
        )

    def get_success_url(self):
        """ Override DatabaseUpdateView default """
        return reverse('db:leader_index', 
                       kwargs={'trips_year': self.kwargs['trips_year']})


class UpdateLeaderWithAssignedTrip(ApplicationEditPermissionRequired, 
                                   FormValidMessageMixin, TripsYearMixin, 
                                   UpdateView):
    """ 
    Add an assigned_trip to a leader. 

    POST target for AssignTripLeaderView 
    """
    model = GeneralApplication
    form_class = TripLeaderAssignmentForm
    lookup_url_kwarg = 'leader_pk'
    template_name = 'db/update.html'

    def get_form_valid_message(self):
        """ Flash success message """
        return '{} assigned to lead {}'.format(
            self.object.applicant, self.object.assigned_trip
        )

    def get_success_url(self):
        """ Override DatabaseUpdateView default """
        return reverse('db:leader_index', 
                       kwargs={'trips_year': self.kwargs['trips_year']})


class RemoveAssignedTrip(ApplicationEditPermissionRequired,
                         FormValidMessageMixin, TripsYearMixin, UpdateView):
    """ Remove a leader's assigned trip """

    model = GeneralApplication
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
        return 'Leader {} removed from Trip {}'.format(
            self.object.applicant, self._assigned_trip
        )
        
    def get_success_url(self):
        return reverse_detail_url(self.object)
    
