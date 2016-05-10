from vanilla import (
    DetailView, CreateView, UpdateView, ListView)
from braces.views import (
    LoginRequiredMixin, GroupRequiredMixin, FormMessagesMixin)
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.db.models import Avg, Value as V
from django.db.models.functions import Coalesce
from django.core.exceptions import PermissionDenied

from fyt.db.views import CrispyFormMixin
from fyt.db.views import TripsYearMixin
from fyt.db.models import TripsYear
from fyt.timetable.models import Timetable
from fyt.trips.models import TripType
from fyt.croos.models import Croo
from fyt.applications.models import GeneralApplication, ApplicationInformation
from fyt.applications.forms import (
    ApplicationForm, CrooSupplementForm,
    LeaderSupplementForm, CertificationForm,
    ApplicationStatusForm, ApplicationAdminForm)
from fyt.applications.filters import ApplicationFilterSet
from fyt.applications.tables import ApplicationTable
from fyt.permissions.views import (
    CreateApplicationPermissionRequired,
    DatabaseReadPermissionRequired,
    ApplicationEditPermissionRequired)
from fyt.utils.views import ExtraContextMixin
from fyt.utils.forms import crispify


class IfApplicationAvailable():
    """
    Restrict application availability based on Timetable dates
    """
    def dispatch(self, request, *args, **kwargs):
        if Timetable.objects.timetable().applications_available():
            return super().dispatch(request, *args, **kwargs)
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

        return super().dispatch(request, *args, **kwargs)

# Form constants
GENERAL_FORM = 'form'
LEADER_FORM = 'leader_form'
CROO_FORM = 'croo_form'


class ApplicationFormsMixin(FormMessagesMixin, CrispyFormMixin):
    """
    View mixin which handles forms for GenearlApplication, LeaderSupplement,
    and CrooSupplement in the same view.
    """
    model = GeneralApplication
    template_name = 'applications/application.html'

    form_valid_message = "Your application has been saved"
    form_invalid_message = (
        "Uh oh. Looks like there's a problem somewhere in your application"
    )

    def get_trips_year(self):
        """
        Override this if the url does not specify a trips year.
        """
        return self.kwargs['trips_year']

    def get(self, request, *args, **kwargs):
        forms = self.get_forms(instances=self.get_instances())
        context = self.get_context_data(**forms)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        forms = self.get_forms(instances=self.get_instances(),
                               data=request.POST, files=request.FILES)
        if all(f.is_valid() for f in forms.values()):
            return self.form_valid(forms)

        return self.form_invalid(forms)

    def get_form_classes(self):
        return {
            GENERAL_FORM: ApplicationForm,
            LEADER_FORM: LeaderSupplementForm,
            CROO_FORM: CrooSupplementForm,
        }

    def get_instances(self):
        """
        Return model instances to populate the forms.
        """
        return {
            GENERAL_FORM: None,
            LEADER_FORM: None,
            CROO_FORM: None
        }

    def get_forms(self, instances,  **kwargs):
        """
        Return a dict mapping form names to form objects.
        """
        trips_year = self.get_trips_year()

        return {name: form_class(instance=instances.get(name), prefix=name,
                                 trips_year=trips_year, **kwargs)
                for name, form_class in self.get_form_classes().items()}

    def form_valid(self, forms):
        """
        Save the forms.
        """
        for form in forms.values():
            form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, forms):
        context = self.get_context_data(**forms)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """
        Lots o' goodies for the template
        """
        trips_year = self.get_trips_year()
        # just in case AppInfo hasn't been setup yet
        information, _ = ApplicationInformation.objects.get_or_create(
            trips_year=trips_year
        )
        return super().get_context_data(
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

    def get_trips_year(self):
        return TripsYear.objects.current()

    def form_valid(self, forms):
        """
        Connect the application instances
        """
        trips_year = self.get_trips_year()
        forms[GENERAL_FORM].instance.applicant = self.request.user
        forms[GENERAL_FORM].instance.trips_year = trips_year
        application = forms[GENERAL_FORM].save()

        forms[LEADER_FORM].instance.application = application
        forms[LEADER_FORM].instance.trips_year = trips_year
        forms[LEADER_FORM].save()

        forms[CROO_FORM].instance.application = application
        forms[CROO_FORM].instance.trips_year = trips_year
        forms[CROO_FORM].save()

        return HttpResponseRedirect(self.get_success_url())


class ContinueApplication(LoginRequiredMixin, IfApplicationAvailable,
                          ApplicationFormsMixin, UpdateView):
    """
    View for applicants to edit their application.
    """
    success_url = reverse_lazy('applications:continue')

    def get_trips_year(self):
        return TripsYear.objects.current()

    def get_object(self):
        """
        TODO: perhaps redirect to NewApplication instead of 404?
        """
        return get_object_or_404(
            self.model,
            applicant=self.request.user,
            trips_year=self.get_trips_year()
        )

    def get_instances(self):
        self.object = self.get_object()
        return {
            GENERAL_FORM: self.object,
            LEADER_FORM: self.object.leader_supplement,
            CROO_FORM: self.object.croo_supplement,
        }


class SetupApplication(CreateApplicationPermissionRequired,
                       ExtraContextMixin, CrispyFormMixin, UpdateView):
    """
    Let directors create/edit this year's application

    Used by directors to edit application questions, general information.

    TOOD: show previous year's application documents???
    TODO: stick this under the db namespace and use TripsYearMixin.
    """

    model = ApplicationInformation
    template_name = 'applications/setup.html'
    success_url = reverse_lazy('applications:setup')
    fields = '__all__'

    def get_object(self):
        """
        There is only one configuration object for each trips year.
        """
        trips_year = TripsYear.objects.current()
        obj, created = self.model.objects.get_or_create(trips_year=trips_year)
        return obj

    def get_form(self, **kwargs):
        return crispify(super().get_form(**kwargs))

    def extra_context(self):
        return {
            'trips_year': TripsYear.objects.current()
        }


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


class ApplicationIndex(DatabaseReadPermissionRequired, BlockDirectorate,
                       TripsYearMixin, ExtraContextMixin, ListView):
    model = GeneralApplication
    template_name = 'applications/application_index.html'

    def get_queryset(self):
        # Grades are coalesced so that ordering works properly on PostreSQL.
        # Otherwise null values - of ungraded applications - come before the
        # actual grades when ApplicationTable orders by the grades.
        # Note that this issue won't appear on a dev sqlite database.
        return (
            super().get_queryset()
            .annotate(avg_croo_grade=Avg('croo_supplement__grades__grade'))
            .annotate(avg_leader_grade=Avg('leader_supplement__grades__grade'))
            .annotate(normalized_croo_grade=Coalesce('avg_croo_grade', V(0.0)))
            .annotate(normalized_leader_grade=Coalesce('avg_leader_grade', V(0.0)))
        )

    def extra_context(self):
        # TODO: use/make a generic FilterView mixin?
        filter = ApplicationFilterSet(
            self.request.GET, queryset=self.object_list,
            trips_year=self.kwargs['trips_year']
        )
        table = ApplicationTable(filter.qs, self.request)
        return {
            'table': table,
            'application_count': len(filter.qs),
            'applications_filter': filter
        }


class ApplicationDetail(DatabaseReadPermissionRequired, BlockDirectorate,
                        ExtraContextMixin, TripsYearMixin, DetailView):
    model = GeneralApplication
    context_object_name = 'application'
    template_name = 'applications/application_detail.html'

    generalapplication_fields = [
        'class_year',
        'gender',
        'race_ethnicity',
        'hinman_box',
        'phone',
        'summer_address',
        'tshirt_size',
        'from_where',
        'what_do_you_like_to_study',
        'personal_activities',
        'feedback',
        'medical_certifications',
        'medical_experience',
        'peer_training',
        'spring_training_ok',
        'summer_training_ok',
        'hanover_in_fall',
        'role_preference',
        'leadership_style',
        'food_allergies',
        'dietary_restrictions',
        'medical_conditions',
        'epipen',
        'needs',
        'trippee_confidentiality',
        'in_goodstanding_with_college',
        'trainings'
    ]
    leaderapplication_fields = [
        'preferred_sections',
        'available_sections',
        'preferred_triptypes',
        'available_triptypes',
        'relevant_experience',
        'trip_preference_comments',
        'cannot_participate_in',
        'document'
    ]
    trainings_fields = [
        'community_building',
        'risk_management',
        'wilderness_skills',
        'croo_training',
        ('first aid cert', 'get_first_aid_cert')
    ]
    crooapplication_fields = [
        'licensed',
        'college_certified',
        'sprinter_certified',
        'microbus_certified',
        'can_get_certified',
        'safety_lead_willing',
        'kitchen_lead_willing',
        'kitchen_lead_qualifications',
        'document'
    ]

    def extra_context(self):
        return {
            'generalapplication_fields': self.generalapplication_fields,
            'leaderapplication_fields': self.leaderapplication_fields,
            'trainings_fields': self.trainings_fields,
            'crooapplication_fields': self.crooapplication_fields,
            'trip_assignment_url': reverse(
                'db:update_trip_assignment', kwargs=self.kwargs),
            'croo_assignment_url': reverse(
                'db:update_croo_assignment', kwargs=self.kwargs)
        }


class ApplicationUpdate(ApplicationEditPermissionRequired,
                        BlockDirectorate, ApplicationFormsMixin,
                        TripsYearMixin, UpdateView):

    template_name = 'applications/application_update.html'
    context_object_name = 'application'

    def get_instances(self):

        self.object = self.get_object()
        return {
            GENERAL_FORM: self.object,
            LEADER_FORM: self.object.leader_supplement,
            CROO_FORM: self.object.croo_supplement,
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
                             BlockDirectorate, ExtraContextMixin,
                             TripsYearMixin, UpdateView):
    """
    Update status, trip/croo assignment etc.
    """
    model = GeneralApplication
    template_name = 'db/update.html'
    fields = ['status', 'assigned_trip', 'assigned_croo', 'safety_lead']
    form_class = ApplicationAdminForm

    def extra_context(self):
        return {
            'preferred_trips': self.object.get_preferred_trips(),
            'available_trips': self.object.get_available_trips(),
            'croos': Croo.objects.filter(
                trips_year=self.kwargs['trips_year']).all(),
        }
