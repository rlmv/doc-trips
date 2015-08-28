from statistics import mean
from collections import defaultdict, OrderedDict

from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Avg
from django.utils.safestring import mark_safe
from django.forms.models import modelformset_factory
from django.shortcuts import get_object_or_404
from vanilla import FormView, UpdateView, TemplateView
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from braces.views import FormValidMessageMixin, SetHeadlineMixin

from doc.trips.models import (
    Trip, TripTemplate, TripType, Campsite, Section,
    NUM_BAGELS_SUPPLEMENT, NUM_BAGELS_REGULAR
)
from doc.trips.forms import (
    TripLeaderAssignmentForm, SectionForm, AssignmentForm,
    TrippeeAssignmentForm, FoodboxFormsetHelper
)
from doc.applications.models import LeaderSupplement, GeneralApplication
from doc.incoming.models import IncomingStudent, Registration
from doc.db.views import (
    DatabaseCreateView, DatabaseUpdateView, DatabaseDeleteView,
    DatabaseListView, DatabaseDetailView, DatabaseTemplateView,
    TripsYearMixin
)
from doc.permissions.views import (
    ApplicationEditPermissionRequired, DatabaseReadPermissionRequired,
    DatabaseEditPermissionRequired
)
from doc.db.urlhelpers import reverse_detail_url
from doc.utils.forms import crispify
from doc.utils.views import PopulateMixin
from doc.utils.cache import cache_as
from doc.transport.models import ExternalBus, ScheduledTransport


class _SectionMixin():
    """
    Utility mixin for CBVs which have a section_pk url kwarg.
    """
    @cache_as('_section')
    def get_section(self):
        return Section.objects.get(pk=self.kwargs['section_pk'])

    def get_context_data(self, **kwargs):
        kwargs['section'] = self.get_section()
        return super(_SectionMixin, self).get_context_data(**kwargs)


class _TripMixin():
    """
    Mixin to pull a trip object from a trip_pk url kwarg
    """
    @cache_as('_trip')
    def get_trip(self):
        return Trip.objects.get(pk=self.kwargs['trip_pk'])

    def get_context_data(self, **kwargs):
        kwargs['trip'] = self.get_trip()
        return super(_TripMixin, self).get_context_data(**kwargs)


class TripList(DatabaseTemplateView):
    template_name = 'trips/trip_index.html'

    def extra_context(self):
        return {'matrix': Trip.objects.matrix(self.kwargs['trips_year'])}


class TripUpdate(DatabaseUpdateView):
    model = Trip
    fields = [
        'dropoff_time', 'pickup_time',
        'dropoff_route', 'pickup_route', 'return_route',
        'notes'
    ]

    def get_headline(self):
        return mark_safe(
            "Edit %s <small> Trip </small>" % self.object
        )


class TripDetail(DatabaseDetailView):
    model = Trip
    template_name = 'trips/trip_detail.html'

    fields = [
        'section', 'template',
        'leaders', 'trippees',
        'notes',
        ('dropoff route', 'get_dropoff_route'),
        'dropoff_time',
        ('pickup route', 'get_pickup_route'),
        'pickup_time',
        ('return route', 'get_return_route')
    ]

    triptemplate_fields = [
        'triptype', 'max_trippees',
        'non_swimmers_allowed',
        'desc_intro',
        'dropoff_stop', 'desc_day1', 'campsite1',
        'desc_day2', 'campsite2',
        'desc_day3', 'pickup_stop',
        'desc_conc', 
        'revisions']
    

class TripCreate(PopulateMixin, DatabaseCreateView):
    model = Trip
    fields = ['section', 'template']
        

class TripDelete(DatabaseDeleteView):
    model = Trip
    success_url_pattern = 'db:trip_index'


class TripTemplateList(DatabaseListView):
    model = TripTemplate
    context_object_name = 'templates' 
    template_name = 'trips/template_index.html'
    
    def get_queryset(self):
        qs = super(TripTemplateList, self).get_queryset()
        return qs.select_related(
            'triptype', 'campsite1', 'campsite2', 'dropoff_stop', 'pickup_stop'
        )


class TripTemplateCreate(DatabaseCreateView):
    model = TripTemplate


class TripTemplateDetail(DatabaseDetailView):
    model = TripTemplate
    fields = ['name', 'description_summary', 'triptype', 
              'max_trippees', 'non_swimmers_allowed', 'dropoff_stop',
              'campsite1', 'campsite2', 'pickup_stop', 'return_route',
              'desc_intro', 'desc_day1',
              'desc_day2', 'desc_day3',
              'desc_conc', 'revisions']


class TripTemplateUpdate(DatabaseUpdateView):
    model = TripTemplate


class TripTemplateDelete(DatabaseDeleteView):
    model = TripTemplate
    success_url_pattern = 'db:triptemplate_index'
    

class TripTypeList(DatabaseListView):
    model = TripType
    context_object_name = 'triptypes'
    template_name = 'trips/triptype_index.html'


class TripTypeCreate(DatabaseCreateView):
    model = TripType


class TripTypeDetail(DatabaseDetailView):
    model = TripType
    fields = ['name', 'trippee_description', 'leader_description',
              'packing_list']


class TripTypeUpdate(DatabaseUpdateView):
    model = TripType


class TripTypeDelete(DatabaseDeleteView):
    model = TripType
    success_url_pattern = 'db:triptype_index'


class CampsiteList(DatabaseListView):
    model = Campsite
    context_object_name = 'campsites'
    template_name = 'trips/campsite_index.html'

    def extra_context(self):
        return {
            'camping_dates': Section.dates.camping_dates(self.kwargs['trips_year'])
        }


class CampsiteCreate(DatabaseCreateView):
    model = Campsite


class CampsiteDetail(DatabaseDetailView):
    model = Campsite
    fields = ['name', 'capacity', 'directions', 'bugout', 'secret']


class CampsiteUpdate(DatabaseUpdateView):
    model = Campsite


class CampsiteDelete(DatabaseDeleteView):
    model = Campsite
    success_url_pattern = 'db:campsite_index'


class SectionList(DatabaseListView):
    model = Section
    context_object_name = 'sections'
    template_name = 'trips/section_index.html'


class SectionCreate(DatabaseCreateView):
    model = Section
    form_class = SectionForm
    template_name = 'trips/section_create.html'


class SectionDetail(DatabaseDetailView):
    model = Section
    fields = ['name', 'leaders_arrive', 'is_local', 'is_exchange', 
              'is_transfer', 'is_international', 'is_native', 'is_fysep']


class SectionUpdate(DatabaseUpdateView):
    model = Section
    form_class = SectionForm
    template_name = 'trips/section_update.html'


class SectionDelete(DatabaseDeleteView):
    model = Section
    success_url_pattern = 'db:section_index'
                               

class LeaderTrippeeIndexView(DatabaseListView):
    """ 
    Show all Trips with leaders and trippees.
    
    Links to pages to assign leaders and trippees.
    """
    model = Trip
    template_name = 'trips/leaders.html'
    context_object_name = 'trips'
    
    def get_queryset(self):
        return (
            super(LeaderTrippeeIndexView, self).get_queryset()
            .prefetch_related('leaders', 'leaders__applicant', 'trippees')
        )

FIRST_CHOICE = 'first choice'
PREFER = 'prefer'
AVAILABLE = 'available'


class AssignTrippee(_TripMixin, DatabaseListView):
    """ 
    Assign trippees to a trip.

    The trip's pk is passed in the url arg.
    """
    model = IncomingStudent
    template_name = 'trips/assign_trippee.html'
    context_object_name = 'available_trippees'

    def get_queryset(self):
        """ 
        All trippees which prefer, are available, or chose this
        trip as their first choice.

        All students in the qs have a registration attached.
        """
        return (self.model.objects.available_for_trip(self.get_trip())
                .select_related(
                    'trip_assignment__template',
                    'trip_assignment__section',
                    'registration__bus_stop')
                .only(
                    'name',
                    'address',
                    'trips_year',
                    'trip_assignment__template__name',
                    'trip_assignment__section__name',
                    'trip_assignment__trips_year',
                    'registration__bus_stop__route_id',
                    'registration__bus_stop__trips_year_id',
                    'registration__bus_stop__name',
                    'registration__gender',
                )
            )

    def get_context_data(self, **kwargs):
        context = super(AssignTrippee, self).get_context_data(**kwargs)
        context['trip'] = trip = self.get_trip()

        # TODO: refactor this...
        triptype = trip.template.triptype
        triptype_preference = {}
        for pair in Registration.available_triptypes.through.objects.filter(triptype=triptype):
            triptype_preference[pair.registration_id] = AVAILABLE
        for pair in Registration.preferred_triptypes.through.objects.filter(triptype=triptype):
            triptype_preference[pair.registration_id] = PREFER
        for registration in Registration.objects.filter(trips_year=self.get_trips_year()):
            if registration.firstchoice_triptype_id == triptype.id:
                triptype_preference[registration.id] = FIRST_CHOICE

        # TODO: refactor this...
        section = trip.section
        section_preference = {}
        for pair in Registration.available_sections.through.objects.filter(section=section):
            section_preference[pair.registration_id] = AVAILABLE
        for pair in Registration.preferred_sections.through.objects.filter(section=section):
            section_preference[pair.registration_id] = PREFER
        
        # compute all external bus routes for this section
        buses = ExternalBus.objects.filter(
            trips_year=self.get_trips_year(), section=section
        )
        route_ids = list(map(lambda bus: bus.route_id, buses))
        
        for trippee in self.object_list:
            url = reverse('db:assign_trippee_to_trip', kwargs={
                'trips_year': self.get_trips_year(),
                'trippee_pk': trippee.pk
            })
            trippee.assignment_url = '%s?assign_to=%s' % (url, trip.pk)
            trippee.triptype_preference = triptype_preference[trippee.registration.id]
            trippee.section_preference = section_preference[trippee.registration.id]
            if trippee.registration.bus_stop:
                trippee.bus_available = trippee.registration.bus_stop.route_id in route_ids
        return context


class AssignTrippeeToTrip(FormValidMessageMixin, DatabaseUpdateView):

    model = IncomingStudent
    lookup_url_kwarg = 'trippee_pk'
    template_name = 'db/update.html'
    form_class = TrippeeAssignmentForm

    def get(self, request, *args, **kwargs):
        """ Pull the 'assign_to' trip from GET qs """
        data = {'trip_assignment': request.GET['assign_to']}
        form = self.get_form(data=data)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_form(self, **kwargs):
        return self.get_form_class()(self.get_trips_year(), **kwargs)
    
    def get_form_valid_message(self):
        """ Flash success message """
        return '{} assigned to {}'.format(
            self.object, self.object.trip_assignment
        )

    def get_headline(self):
        self.object = self.get_object()
        return 'Assign {} to trip'.format(self.object)

    def get_success_url(self):
        """ Override DatabaseUpdateView default """
        return reverse('db:leader_index',
                       kwargs={'trips_year': self.get_trips_year()})


class AssignTripLeaderView(_TripMixin, DatabaseListView):
    """ 
    Assign a leader to a Trip.

    Takes the trip's pk as a url arg.
    The template is passed a list of tuples in context_object_name:
    (LeaderApplication, assign_link, triptype_preference, section_pref)
    - assign_link will be None if the leader is already assigned to a trip.
    - triptype_preference is a string describing whether the leader prefers or
    is available for the trip type
    - section preference is a string describing whether the leader prefers or 
    is available for the section.
    """
    model = GeneralApplication
    template_name = 'trips/assign_leader.html'
    context_object_name = 'leader_applications'

    def get_queryset(self):
        qs = (
            self.model.objects.prospective_leaders_for_trip(self.get_trip())
            .select_related(
                'applicant',
                'assigned_trip',
                'assigned_trip__template',
                'assigned_trip__section'
            ).prefetch_related(
                'leader_supplement__grades'
            ).only(
                'trips_year', 'gender',
                'applicant__name',
                'assigned_trip__trips_year_id',
                'assigned_trip__template__name',
                'assigned_trip__section__name',
                'status'
            )
        )

        # For some reason, annotating grades using Avg adds an 
        # expensive GROUP BY clause to the query, killing the site.
        # See https://code.djangoproject.com/ticket/17144. 
        # Does this need to be reopened?
        # TODO: check with 1.8
        # This is a hackish workaround to explicitly compute the
        # average for all applications with reasonable performance:
        for app in qs:
            if app.leader_supplement.grades.exists():
                app.avg_grade = mean(
                    map(lambda g: g.grade, app.leader_supplement.grades.all())
                )
            else:
                app.avg_grade = None
        # return 0 in case someone has no grades
        return sorted(qs, key=lambda x: x.avg_grade or 0, reverse=True)

    def get_assign_url(self, leader, trip):
        """ Return the url used to assign leader to trip """
        url = reverse('db:assign_leader_to_trip', kwargs={
            'trips_year': self.kwargs['trips_year'],
            'leader_pk': leader.pk
        })
        return '%s?assign_to=%s' % (url, trip.pk)

    def get_context_data(self, **kwargs):
        context = super(AssignTripLeaderView, self).get_context_data(**kwargs)
        context['trip'] = trip = self.get_trip()

        # Compute whether each leader prefers or is available for this 
        # trip's section and triptype. We do this because prefetch_related
        # pulls in *all* related objects--and all fields of the related 
        # objects--which is a huge query and kills performance.
        # This technique is O(1) for queries and O(n) for in-memory 
        # processing, which is quite acceptable.
        # PREFERing takes precedence; if a leader both prefers and is 
        # available we just show that she prefers the option.
        # See http://stackoverflow.com/questions/10273744/django-many-to-many-field-prefetch-primary-keys-only

        triptype = trip.template.triptype
        triptype_preference = {}
        for pair in LeaderSupplement.available_triptypes.through.objects.filter(triptype=triptype):
            triptype_preference[pair.leadersupplement_id] = AVAILABLE
        for pair in LeaderSupplement.preferred_triptypes.through.objects.filter(triptype=triptype):
            triptype_preference[pair.leadersupplement_id] = PREFER

        section_preference = {}
        section = trip.section
        for pair in LeaderSupplement.available_sections.through.objects.filter(section=section):
            section_preference[pair.leadersupplement_id] = AVAILABLE
        for pair in LeaderSupplement.preferred_sections.through.objects.filter(section=section):
            section_preference[pair.leadersupplement_id] = PREFER

        def process_leader(leader):
            if leader.assigned_trip:
                link = None
            else:
                link = self.get_assign_url(leader, trip)
            return (leader, link, triptype_preference[leader.id],
                    section_preference[leader.id])

        context[self.context_object_name] = list(map(process_leader, self.object_list))
        return context

# should these volunteer specific views go to the applications app?

class AssignLeaderToTrip(ApplicationEditPermissionRequired,
                         FormValidMessageMixin, TripsYearMixin, UpdateView):

    model = GeneralApplication
    lookup_url_kwarg = 'leader_pk'
    template_name = 'db/update.html'
    form_class = AssignmentForm

    def get(self, request, *args, **kwargs):
        """ Pull the 'assign_to' trip from GET qs """
        data = {'assigned_trip': request.GET['assign_to']}
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


class RemoveAssignedTrip(ApplicationEditPermissionRequired,
                         FormValidMessageMixin, TripsYearMixin, UpdateView):
    """ Remove a leader's assigned trip """

    model = GeneralApplication
    lookup_url_kwarg = 'leader_pk'
    template_name = 'trips/remove_leader_assignment.html'

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


class TrippeeLeaderCounts(DatabaseTemplateView):
    """
    Shows a matrix of the number of tripees and leaders for all trips
    """
    template_name = 'trips/trippee_leader_counts.html'

    def extra_context(self):
        return {
            'matrix': Trip.objects.matrix(self.kwargs['trips_year'])
        }


class FoodboxCounts(DatabaseListView):

    model = Trip
    template_name = 'trips/foodboxes.html'
    context_object_name = 'trips'

    def get_queryset(self):
        return Trip.objects.filter(
            trips_year=self.kwargs['trips_year']
        ).select_related(
            'template__triptype'
        )

    def extra_context(self):
        qs = self.object_list
        return {
            'full': len(qs),
            'half': len(list(filter(lambda x: x.half_foodbox, qs))),
            'supp': len(list(filter(lambda x: x.supp_foodbox, qs))),
            'bagels': sum(map(lambda x: x.bagels, qs)),
            'bagel_ratio': NUM_BAGELS_REGULAR,
            'supp_bagel_ratio': NUM_BAGELS_SUPPLEMENT,
        }


class FoodboxRules(DatabaseEditPermissionRequired, TripsYearMixin, FormView):

    template_name = 'trips/foodbox_rules.html'

    def get_queryset(self):
        return TripType.objects.filter(trips_year=self.kwargs['trips_year'])
    
    def get_form(self, **kwargs):
        FoodRulesFormset = modelformset_factory(
            TripType, fields=['name', 'half_kickin', 'gets_supplemental'],
            extra=0
        )
        formset = FoodRulesFormset(queryset=self.get_queryset(), **kwargs)
        formset.helper = FoodboxFormsetHelper()
        formset.helper.form_class = 'form-inline'
        formset.helper.add_input(Submit('submit', 'Save'))
        return formset

    def form_valid(self, formset):
        formset.save()
        return super(FoodboxRules, self).form_valid(formset)
       
    def get_success_url(self):
        return self.request.path


class LeaderPacket(DatabaseDetailView):
    """
    All information that leader's need: schedule, directions, 
    medical info, etc.
    """
    model = Trip
    template_name = 'trips/leader_packet.html'


class PacketsForSection(_SectionMixin, DatabaseListView):
    """
    All leader packets for a section.
    """
    model = Trip
    template_name = 'trips/section_packet.html'
    context_object_name = 'trips'

    def get_queryset(self):
        return super(PacketsForSection, self).get_queryset().filter(
            section=self.get_section()
        ).select_related(
            'template__campsite1',
            'template__campsite2',
            'template__dropoff_stop',
            'template__pickup_stop'
        ).prefetch_related(
            'leaders',
            'leaders__applicant',
            'trippees',
            'trippees__registration'
        )


class MedicalInfoForSection(PacketsForSection):
    """
    Packets for croos, by section.
    
    Contains leader and trippee med information.
    """
    template_name = 'trips/medical_packet.html'


class TrippeeChecklist(_SectionMixin, DatabaseListView):
    """
    Checklist of a trippees for a section.
    """
    model = IncomingStudent
    template_name = 'trips/person_checklist.html'
    header_text = 'Trippee'

    def get_queryset(self):
        qs = super(TrippeeChecklist, self).get_queryset()
        return qs.filter(trip_assignment__section=self.get_section())


class LeaderChecklist(_SectionMixin, DatabaseListView):
    """
    All leaders for a section.
    """
    model = GeneralApplication
    template_name = 'trips/person_checklist.html'
    header_text = 'Leader'

    def get_queryset(self):
        qs = super(LeaderChecklist, self).get_queryset()
        return qs.filter(assigned_trip__section=self.get_section())
   

class Checklists(DatabaseTemplateView):
    """
    Central list of all checklists"
    """
    template_name = 'trips/checklists.html'

    def extra_context(self):

        trips_year = self.kwargs['trips_year']

        dates = Section.dates.leader_dates(trips_year)
        d = OrderedDict([date, []] for date in dates)

        for sxn in Section.objects.filter(trips_year=trips_year):
            kwargs = {
                'trips_year': trips_year,
                'section_pk': sxn.pk
            }
            d[sxn.leaders_arrive].append((
                'Section %s Leader Checkin' % sxn.name,
                reverse('db:checklists:leaders', kwargs=kwargs)))

            d[sxn.trippees_arrive].append((
                'Section %s Trippee Checkin' % sxn.name,
                reverse('db:checklists:trippees', kwargs=kwargs)))
            
            d[sxn.trippees_arrive].append((
                'Section %s Leader Packets' % sxn.name,
                reverse('db:packets:section', kwargs=kwargs)))

            d[sxn.trippees_arrive].append((
                'Section %s Medical Information' % sxn.name,
                reverse('db:packets:medical', kwargs=kwargs)))

        buses = ScheduledTransport.objects.filter(trips_year=trips_year)
        for date in set(map(lambda x: x.date, buses)):
            d[date].append((
                'Internal Bus Directions for %s' % date.strftime('%m/%d'),
                reverse('db:internal_packet_for_date', kwargs={
                    'trips_year': trips_year, 'date': date
                })
            ))

        buses = ExternalBus.objects.filter(trips_year=trips_year)
        route_dict = defaultdict(set)
        for bus in buses:
            route_dict[bus.date_to_hanover].add(bus.route)
            route_dict[bus.date_from_hanover].add(bus.route)
        for date, routes in route_dict.items():
            for route in routes:
                d[date].append((
                    '%s Directions for %s' % (route, date.strftime('%m/%d')),
                    reverse('db:external_packet_for_date_and_route', kwargs={
                        'trips_year': trips_year, 'date': date, 'route_pk': route.pk
                    })
                ))
       
        return {'date_dict': d}
