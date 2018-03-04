from braces.views import (
    FormMessagesMixin,
    FormValidMessageMixin,
    GroupRequiredMixin,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from vanilla import CreateView, DetailView, FormView, ListView, UpdateView

from fyt.applications.filters import ApplicationFilterSet
from fyt.applications.forms import (
    AgreementForm,
    ApplicationAdminForm,
    ApplicationForm,
    ApplicationStatusForm,
    CrooSupplementForm,
    LeaderSupplementForm,
    QuestionForm,
)
from fyt.applications.models import ApplicationInformation, Question, Volunteer
from fyt.applications.tables import ApplicationTable
from fyt.core.models import TripsYear
from fyt.core.views import CrispyFormMixin, TripsYearMixin
from fyt.croos.models import Croo
from fyt.permissions.permissions import groups
from fyt.permissions.views import (
    ApplicationEditPermissionRequired,
    DatabaseReadPermissionRequired,
    SettingsPermissionRequired,
)
from fyt.timetable.models import Timetable
from fyt.training.forms import FirstAidCertificationFormset
from fyt.trips.models import TripType
from fyt.utils.cache import preload
from fyt.utils.forms import crispify
from fyt.utils.views import ExtraContextMixin


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
QUESTION_FORM = 'question_form'
AGREEMENT_FORM = 'agreement_form'
FIRST_AID_FORM = 'first_aid_form'

FORM_ORDERING = [
    FIRST_AID_FORM,
    GENERAL_FORM,
    LEADER_FORM,
    CROO_FORM,
    QUESTION_FORM,
    AGREEMENT_FORM
]


def order_forms(forms):
    """Convert a dict of forms into a list to pass to the context."""
    return [forms[name] for name in FORM_ORDERING]


class ApplicationFormsMixin(FormMessagesMixin, CrispyFormMixin):
    """
    View mixin which handles forms for GenearlApplication, LeaderSupplement,
    and CrooSupplement in the same view.
    """
    model = Volunteer
    context_object_name = 'application'
    template_name = 'applications/application.html'

    form_valid_message = "Your application has been saved"
    form_invalid_message = (
        "Uh oh, it looks like there's a problem with your application"
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
            AGREEMENT_FORM: AgreementForm,
            LEADER_FORM: LeaderSupplementForm,
            CROO_FORM: CrooSupplementForm,
            QUESTION_FORM: QuestionForm,
            FIRST_AID_FORM: FirstAidCertificationFormset
        }

    def get_instances(self):
        """
        Return model instances to populate the forms.
        """
        return {
            GENERAL_FORM: None,
            LEADER_FORM: None,
            CROO_FORM: None,
            QUESTION_FORM: None,
            AGREEMENT_FORM: None,
            FIRST_AID_FORM: None
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
        self.messages.success(self.get_form_valid_message())
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, forms):
        self.messages.error(self.get_form_invalid_message())
        context = self.get_context_data(form_invalid=True, **forms)
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
            forms=order_forms(kwargs),
            trips_year=trips_year,
            timetable=Timetable.objects.timetable(),
            information=information,
            triptypes=TripType.objects.visible(trips_year),
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

        forms[GENERAL_FORM].update_agreements(forms[AGREEMENT_FORM])
        forms[GENERAL_FORM].instance.applicant = self.request.user
        forms[GENERAL_FORM].instance.trips_year = trips_year
        application = forms[GENERAL_FORM].save()

        forms[QUESTION_FORM].instance = application
        forms[QUESTION_FORM].save()

        forms[LEADER_FORM].instance.application = application
        forms[LEADER_FORM].instance.trips_year = trips_year
        forms[LEADER_FORM].save()

        forms[CROO_FORM].instance.application = application
        forms[CROO_FORM].instance.trips_year = trips_year
        forms[CROO_FORM].save()

        forms[FIRST_AID_FORM].instance = application
        forms[FIRST_AID_FORM].save()

        self.messages.success(self.get_form_valid_message())
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
            AGREEMENT_FORM: self.object,
            QUESTION_FORM: self.object,
            LEADER_FORM: self.object.leader_supplement,
            CROO_FORM: self.object.croo_supplement,
            FIRST_AID_FORM: self.object
        }


class SetupApplication(SettingsPermissionRequired, ExtraContextMixin,
                       FormValidMessageMixin, CrispyFormMixin, UpdateView):
    """
    Let directors create/edit this year's application

    Used by directors to edit application questions, general information.

    TODO: stick this under the db namespace and use TripsYearMixin.
    """

    model = ApplicationInformation
    template_name = 'applications/setup.html'
    success_url = reverse_lazy('applications:setup')
    fields = [
        'application_header'
    ]
    form_valid_message = "Application successfully updated"

    def get_object(self):
        """
        There is only one configuration object for each trips year.
        """
        trips_year = TripsYear.objects.current()
        obj, created = self.model.objects.get_or_create(trips_year=trips_year)
        return obj

    def get_form(self, **kwargs):
        return crispify(super().get_form(**kwargs), submit_text='Save')

    def extra_context(self):
        trips_year = TripsYear.objects.current()
        return {
            'trips_year': trips_year,
            'questions': Question.objects.filter(trips_year=trips_year)
        }


QuestionFormset = forms.models.modelformset_factory(
    Question, extra=6, fields='__all__', can_delete=True
)


class EditQuestions(SettingsPermissionRequired, FormValidMessageMixin, FormView):
    template_name = 'applications/questions.html'
    success_url = reverse_lazy('applications:setup')
    form_valid_message = "Application successfully updated"

    def get_trips_year(self):
        return TripsYear.objects.current()

    def get_queryset(self):
        trips_year = self.get_trips_year()
        return Question.objects.filter(trips_year=trips_year)

    def get_form(self, **kwargs):
        formset = QuestionFormset(queryset=self.get_queryset(), **kwargs)
        formset.helper = FormHelper()
        formset.helper.add_input(Submit('submit', 'Save'))
        return formset

    def form_valid(self, formset):
        # Add trips_year to new questions
        trips_year = self.get_trips_year()
        for form in formset.extra_forms:
            if form.has_changed():
                form.instance.trips_year = trips_year

        formset.save()
        return super().form_valid(formset)


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


# TODO: move to queryset method
def preload_questions(qs, trips_year):
    """
    Preload the _required_questions cache on a queryset of applications so that
    `leader_application_complete` and `croo_application_complete` can be
    efficiently computed.
    """
    questions = Question.objects.filter(trips_year=trips_year)

    for app in qs:
        preload(app, app.REQUIRED_QUESTIONS, questions)

    return qs


class BlockOldApplications():
    """
    Only allow grading once applications are closed
    """
    not_available_template = 'applications/old_applications_not_available.html'

    def dispatch(self, request, *args, **kwargs):
        # TODO: yuck, implement this as a utility method
        if (TripsYear.objects.current().year != int(self.get_trips_year()) and
                groups.directors not in request.user.groups.all()):
            raise PermissionDenied('Only Trip Directors can view applications '
                                   'from previous years.')
        return super().dispatch(request, *args, **kwargs)


class ApplicationIndex(DatabaseReadPermissionRequired, BlockDirectorate,
                       BlockOldApplications, TripsYearMixin,
                       ExtraContextMixin, ListView):
    model = Volunteer
    template_name = 'applications/application_index.html'

    def get_queryset(self):
        return Volunteer.objects.with_scores(
            self.kwargs['trips_year']
        ).only(
            'applicant__netid',
            'applicant__name',
            'trips_year_id',
            'status',
            'gender',
            'leader_willing',
            'croo_willing',
        ).prefetch_related(
            'answer_set'
        )

    def extra_context(self):
        # TODO: use/make a generic FilterView mixin?
        filter = ApplicationFilterSet(
            self.kwargs['trips_year'], self.request.GET,
            queryset=self.object_list
        )
        filter_qs = preload_questions(filter.qs, self.kwargs['trips_year'])
        table = ApplicationTable(filter_qs, self.request)
        return {
            'table': table,
            'application_count': len(filter_qs),
            'applications_filter': filter
        }


class ApplicationDetail(DatabaseReadPermissionRequired, BlockDirectorate,
                        BlockOldApplications, ExtraContextMixin,
                        TripsYearMixin, DetailView):
    model = Volunteer
    context_object_name = 'application'
    template_name = 'applications/application_detail.html'

    volunteer_fields = [
        ('Applying for trip leader','leader_willing'),
        ('Applying for croo', 'croo_willing'),
        'class_year',
        'gender',
        'race_ethnicity',
        'hinman_box',
        'phone',
        'summer_address',
        'tshirt_size',
        'height',  # TODO: gear app
        'weight',  # TODO
        'gear',    # TODO
        'hometown',
        'what_do_you_like_to_study',
        'personal_activities',
        'feedback',
        'medical_certifications',
        'medical_experience',
        'peer_training',
        'spring_training_ok',
        'summer_training_ok',
        'hanover_in_fall',
        'transfer_exchange',
        'role_preference',
        'food_allergies',
        'dietary_restrictions',
        'medical_conditions',
        'epipen',
        'needs',
        'trippee_confidentiality',
        'in_goodstanding_with_college',
        'trainings',
    ]
    leaderapplication_fields = [
        ('preferred sections', 'new_preferred_sections'),
        ('available sections', 'new_available_sections'),
        ('preferred trip types', 'new_preferred_triptypes'),
        ('available trip types', 'new_available_triptypes'),
        'class_2_3_paddler',
        'ledyard_level_1',
        'ledyard_level_2',
        'paddling_experience',
        'climbing_course',
        'dmc_leader',
        'climbing_experience',
        'dmbc_leader',
        'biking_experience',
        'bike_maintenance_experience',
        'cnt_leader',
        'hiking_experience',
        'relevant_experience',
        'availability',
        'section_availability',
        'co_leader',
        '_old_document'  # Deprecated field - include conditionally?
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
        '_old_document'  # Deprecated field - include conditionally?
    ]

    def extra_context(self):
        return {
            'volunteer_fields': self.volunteer_fields,
            'leaderapplication_fields': self.leaderapplication_fields,
            'trainings_fields': self.trainings_fields,
            'crooapplication_fields': self.crooapplication_fields,
            'trip_assignment_url': reverse(
                'core:volunteer:update_trip', kwargs=self.kwargs),
            'croo_assignment_url': reverse(
                'core:volunteer:update_croo', kwargs=self.kwargs)
        }


class ApplicationUpdate(ApplicationEditPermissionRequired, BlockDirectorate,
                        BlockOldApplications, ApplicationFormsMixin,
                        TripsYearMixin, UpdateView):
    template_name = 'applications/application_update.html'

    def get_form_valid_message(self):
        return "Succesfully updated {}'s application".format(
            self.object.applicant.name)

    def get_instances(self):
        self.object = self.get_object()
        return {
            GENERAL_FORM: self.object,
            LEADER_FORM: self.object.leader_supplement,
            CROO_FORM: self.object.croo_supplement,
            AGREEMENT_FORM: self.object,
            QUESTION_FORM: self.object
        }

    def get_context_data(self, **kwargs):
        """
        Override ApplicationFormsMixin get_context_data
        """
        trips_year = self.kwargs['trips_year']
        info = ApplicationInformation.objects.get(trips_year=trips_year)
        return super(ApplicationFormsMixin, self).get_context_data(
            forms=order_forms(kwargs),
            trips_year=trips_year, information=info,
            triptypes=TripType.objects.visible(trips_year),
            **kwargs
        )


class ApplicationStatusUpdate(ApplicationEditPermissionRequired,
                              BlockDirectorate, BlockOldApplications,
                              TripsYearMixin, UpdateView):
    """
    Edit Application status
    """
    model = Volunteer
    form_class = ApplicationStatusForm
    template_name = 'applications/status_update.html'


class ApplicationAdminUpdate(ApplicationEditPermissionRequired,
                             BlockDirectorate, BlockOldApplications,
                             ExtraContextMixin, TripsYearMixin, UpdateView):
    """
    Update status, trip/croo assignment etc.
    """
    model = Volunteer
    template_name = 'core/update.html'
    fields = ['status', 'assigned_trip', 'assigned_croo', 'safety_lead']
    form_class = ApplicationAdminForm

    def extra_context(self):
        return {
            'preferred_trips': self.object.get_preferred_trips(),
            'available_trips': self.object.get_available_trips(),
            'croos': Croo.objects.filter(
                trips_year=self.kwargs['trips_year']).all(),
        }
