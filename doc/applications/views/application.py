from vanilla import (
    DetailView, CreateView, UpdateView, ListView)
from braces.views import (
    LoginRequiredMixin, GroupRequiredMixin, FormMessagesMixin)
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.db.models import Avg
from django.core.exceptions import PermissionDenied

from doc.db.views import CrispyFormMixin
from doc.db.views import TripsYearMixin
from doc.db.models import TripsYear
from doc.timetable.models import Timetable
from doc.trips.models import TripType
from doc.croos.models import Croo
from doc.applications.models import GeneralApplication, ApplicationInformation
from doc.applications.forms import (
    ApplicationForm, CrooSupplementForm,
    LeaderSupplementForm, CertificationForm,
    ApplicationStatusForm, ApplicationAdminForm)
from doc.applications.filters import ApplicationFilterSet
from doc.applications.tables import ApplicationTable
from doc.permissions.views import (
    CreateApplicationPermissionRequired,
    DatabaseReadPermissionRequired,
    ApplicationEditPermissionRequired)
from doc.utils.views import MultipleFormMixin
from doc.utils.forms import crispify


class IfApplicationAvailable():
    """
    Restrict application availability based on Timetable dates
    """
    def dispatch(self, request, *args, **kwargs):
        if Timetable.objects.timetable().applications_available():
            return super(IfApplicationAvailable, self).dispatch(
                request, *args, **kwargs
            )
        return render(request, 'applications/not_available.html')


class ContinueIfAlreadyApplied():
    """
    If user has already applied, redirect to edit existing application.
    
    This lives in a mixin instead of in the NewApplication view because if
    has to follow LoginRequired in the MRO. An AnonymousUser causes the 
    query to throw an error.
    """
    def dispatch(self, request, *args, **kwargs):

        exists = self.model.objects.filter(
            applicant=self.request.user,
            trips_year=TripsYear.objects.current().year
        ).exists()
        if exists:
            return HttpResponseRedirect(reverse('applications:continue'))

        return super(ContinueIfAlreadyApplied, self).dispatch(request, *args, **kwargs)


class ApplicationFormsMixin(FormMessagesMixin, MultipleFormMixin,
                            CrispyFormMixin):
    """
    View mixin which handles forms for Application,
    LeaderSupplement, and CrooSupplement in the same view.
    """
    model = GeneralApplication
    template_name = 'applications/application.html'

    form_valid_message = "Your application has been saved"
    form_invalid_message = (
        "Uh oh. Looks like there's a problem somewhere in your application"
    )

    def get_form_classes(self):
        """
        See utils.views.MultipleFormMixin
        """
        return {
            'form': ApplicationForm,
            'leader_form': LeaderSupplementForm,
            'croo_form': CrooSupplementForm,
        }

    def get_context_data(self, **kwargs):
        """ 
        Lots o' goodies for the template
        """
        trips_year = TripsYear.objects.current()
        # just in case AppInfo hasn't been setup yet
        information, _ = ApplicationInformation.objects.get_or_create(
            trips_year=trips_year
        )
        return super(ApplicationFormsMixin, self).get_context_data(
            trips_year=trips_year,
            timetable=Timetable.objects.timetable(),
            information=information,
            triptypes=TripType.objects.filter(trips_year=trips_year),
            **kwargs
        )
    

class NewApplication(LoginRequiredMixin, IfApplicationAvailable,
                     ContinueIfAlreadyApplied, ApplicationFormsMixin,
                     CreateView):
    """
    Apply for trips
    """
    success_url = reverse_lazy('applications:continue')

    def form_valid(self, forms):
        """ 
        Connect the application instances
        """
        trips_year = TripsYear.objects.current()
        forms['form'].instance.applicant = self.request.user
        forms['form'].instance.trips_year = trips_year
        # form.status??
        application = forms['form'].save()

        forms['leader_form'].instance.application = application
        forms['leader_form'].instance.trips_year = trips_year
        forms['leader_form'].save()

        forms['croo_form'].instance.application = application
        forms['croo_form'].instance.trips_year = trips_year
        forms['croo_form'].save()

        return HttpResponseRedirect(self.get_success_url())


class ContinueApplication(LoginRequiredMixin, IfApplicationAvailable,  
                          ApplicationFormsMixin, UpdateView):
    """ 
    View for applicants to edit their application.
    """
    success_url = reverse_lazy('applications:continue')
    context_object_name = 'application'
    
    def get_object(self):
        """ 
        TODO: perhaps redirect to NewApplication instead of 404?
        """
        return get_object_or_404(
            self.model,
            applicant=self.request.user,
            trips_year=TripsYear.objects.current()
        )

    def get_instances(self):
        self.object = self.get_object()
        return {
            'form': self.object,
            'leader_form': self.object.leader_supplement,
            'croo_form': self.object.croo_supplement,
        }


class SetupApplication(CreateApplicationPermissionRequired,
                       CrispyFormMixin, UpdateView):
    """
    Let directors create/edit this year's application

    Used by directors to edit application questions, general information.

    TOOD: show previous year's application documents???
    TODO: stick this under the db namespace and use TripsYearMixin.
    """

    model = ApplicationInformation
    template_name = 'applications/setup.html'
    success_url = reverse_lazy('applications:setup')

    def get_object(self):
        """ 
        There is only one configuration object for each trips year.
        """
        trips_year = TripsYear.objects.current()
        obj, created = self.model.objects.get_or_create(trips_year=trips_year)
        return obj

    def get_form(self, **kwargs):
        return crispify(super(SetupApplication, self).get_form(**kwargs))

    def get_context_data(self, **kwargs):
        """
        Add current tripsyear to template context 
        """
        context = super(SetupApplication, self).get_context_data(**kwargs)
        context['trips_year'] = TripsYear.objects.current()
        return context


class BlockDirectorate(GroupRequiredMixin):
    """
    Blocks access to directorate if the 'hide_volunteer_page'
    in the Timetable is True.

    This must go *after* permission checks.
    """
    group_required = ['directors', 'trip leader trainers']

    def dispatch(self, request, *args, **kwargs):
        """
        Lifted from the default GroupRequiredMixin.

        We first check whether the volunteer pages should be hidden to
        Directorate members. We drop some of the redirect details
        here because we already know that we're dealing with an
        authenticated user.
        """
        if Timetable.objects.timetable().hide_volunteer_page:
            self.request = request
            in_group = self.check_membership(self.get_group_required())
            if not in_group:
                raise PermissionDenied
        return super(GroupRequiredMixin, self).dispatch(
            request, *args, **kwargs
        )


class ApplicationIndex(DatabaseReadPermissionRequired,
                                  BlockDirectorate, TripsYearMixin, ListView):
    model = GeneralApplication
    context_object_name = 'applications'
    template_name = 'applications/application_index.html'

    def get_queryset(self):
        return (
            super(ApplicationIndex, self).get_queryset()
            .annotate(avg_croo_grade=Avg('croo_supplement__grades__grade'))
            .annotate(avg_leader_grade=Avg('leader_supplement__grades__grade'))
            .select_related('applicant', 'croo_supplement', 'leader_supplement')
        )

    def get_context_data(self, **kwargs):
        
        # TODO: use/make a generic FilterView mixin?
        context = super(ApplicationIndex, self).get_context_data(**kwargs)
        applications_filter = ApplicationFilterSet(
            self.request.GET, queryset=self.object_list,
            trips_year=self.kwargs['trips_year']
        )
        context[self.context_object_name] = applications_filter.qs
        table = ApplicationTable(applications_filter.qs)
        from django_tables2   import RequestConfig
        RequestConfig(self.request, paginate=False).configure(table)
        context['table'] = table
        context['applications_filter'] = applications_filter
        return context


class ApplicationDetail(DatabaseReadPermissionRequired,
                        BlockDirectorate, TripsYearMixin, DetailView):
    model = GeneralApplication
    context_object_name = 'application'
    template_name = 'applications/application_detail.html'

    generalapplication_fields = [
        'class_year', 'gender', 'race_ethnicity',
        'hinman_box', 'phone', 'summer_address',
        'tshirt_size', 'from_where',
        'what_do_you_like_to_study', 'personal_activities',
        'feedback', 'medical_certifications',
        'medical_experience', 'peer_training',
        'spring_training_ok', 'summer_training_ok',
        'hanover_in_fall', 'role_preference',
        'dietary_restrictions', 'allergen_information',
        'trippee_confidentiality',
        'in_goodstanding_with_college', 'trainings'
    ]
    leaderapplication_fields = [
        'preferred_sections', 'available_sections',
        'preferred_triptypes', 'available_triptypes',
        'relevant_experience', 'trip_preference_comments',
        'cannot_participate_in', 'document'
    ]
    trainings_fields = [
        'community_building', 'risk_management',
        'wilderness_skills', 'croo_training',
        ('first aid cert', 'get_first_aid_cert')
    ]
    crooapplication_fields = [
        'safety_lead_willing', 'kitchen_lead_willing',
        'kitchen_lead_qualifications', 'document'
    ]

    def get_context_data(self, **kwargs):
        context = super(ApplicationDetail, self).get_context_data(**kwargs)
        trips_year = self.kwargs['trips_year']
        context['trips_year'] = trips_year
        context['generalapplication_fields'] = self.generalapplication_fields
        context['leaderapplication_fields'] = self.leaderapplication_fields
        context['trainings_fields'] = self.trainings_fields
        context['crooapplication_fields'] = self.crooapplication_fields
        context['trip_assignment_url'] = reverse(
            'db:update_trip_assignment', kwargs=self.kwargs
        )
        context['croo_assignment_url'] = reverse(
            'db:update_croo_assignment', kwargs=self.kwargs
        )
        return context


class ApplicationUpdate(ApplicationEditPermissionRequired,
                        BlockDirectorate, ApplicationFormsMixin,
                        TripsYearMixin, UpdateView):
    
    template_name = 'applications/application_update.html'
    context_object_name = 'application'

    def get_instances(self):

        self.object = self.get_object()
        return {
            'form': self.object,
            'leader_form': self.object.leader_supplement,
            'croo_form': self.object.croo_supplement,
        }


    def get_context_data(self, **kwargs):
        """ 
        Override ApplicationFormsMixin get_context_data
        """
        trips_year = self.kwargs['trips_year']
        info = ApplicationInformation.objects.get(trips_year=trips_year)
        return super(ApplicationFormsMixin, self).get_context_data(
            trips_year=trips_year, information=info,
            triptypes=TripType.objects.filter(trips_year=trips_year),
            **kwargs
        )


class ApplicationStatusUpdate(ApplicationEditPermissionRequired,
                              BlockDirectorate, TripsYearMixin, UpdateView):
    """
    Edit Application status
    """
    model = GeneralApplication
    form_class = ApplicationStatusForm
    template_name = 'applications/status_update.html'


class ApplicationCertsUpdate(ApplicationEditPermissionRequired,
                             BlockDirectorate, TripsYearMixin,
                             UpdateView):
    """
    Edit certifications
    """
    model = GeneralApplication
    form_class = CertificationForm
    template_name = 'applications/trainings_update.html'

    def get_success_url(self):
        """
        Redirect back to GeneralApplication
        """
        return self.object.get_absolute_url()


class ApplicationAdminUpdate(ApplicationEditPermissionRequired,
                             BlockDirectorate, TripsYearMixin, 
                             UpdateView):
    """
    Update status, trip/croo assignment etc.
    """
    model = GeneralApplication
    template_name = 'db/update.html'
    fields = ['status', 'assigned_trip', 'assigned_croo', 'safety_lead']
    form_class = ApplicationAdminForm
    
    def get_context_data(self, **kwargs):
        kwargs['preferred_trips'] = self.object.get_preferred_trips()
        kwargs['available_trips'] = self.object.get_available_trips()
        kwargs['croos'] = Croo.objects.filter(
            trips_year=self.kwargs['trips_year']).all()
        return super(ApplicationAdminUpdate, self).get_context_data(**kwargs)
