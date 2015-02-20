
from vanilla import CreateView, UpdateView, RedirectView, TemplateView
from braces.views import FormMessagesMixin
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib import messages

from db.views import CrispyFormMixin
from db.views import DatabaseListView, DatabaseDetailView, DatabaseUpdateView, DatabaseMixin
from db.models import TripsYear
from db.forms import tripsyear_modelform_factory
from timetable.models import Timetable
from trips.models import TripType
from applications.models import GeneralApplication, LeaderSupplement, CrooSupplement, ApplicationInformation, CrooApplicationGrade, LeaderApplicationGrade
from applications.forms import ApplicationForm, CrooSupplementForm, LeaderSupplementForm, LeaderSupplementAdminForm, CrooApplicationGradeForm
from permissions.views import CreateApplicationsPermissionRequired, CrooGraderPermissionRequired
from utils.views import MultipleFormMixin


class IfApplicationAvailable():

    def dispatch(self, request, *args, **kwargs):
        if Timetable.objects.timetable().applications_available():
            return super(IfApplicationAvailable, self).dispatch(request, *args, **kwargs)
        
        return render(request, 'applications/not_available.html')


class NewApplication(LoginRequiredMixin, IfApplicationAvailable, 
                     CrispyFormMixin, CreateView):

    model = GeneralApplication
    template_name = 'applications/new_application.html'
    success_url = reverse_lazy('applications:continue')

    def dispatch(self, request, *args, **kwargs):
        """ If user has already applied, redirect to edit existing application """

        if self.model.objects.filter(applicant=self.request.user, 
                                      trips_year=TripsYear.objects.current()).exists():
            return HttpResponseRedirect(self.get_success_url())

        return super(NewApplication, self).dispatch(request, *args, **kwargs)

    def get_form(self, **kwargs):

        form = ApplicationForm(**kwargs)
        form.helper.form_tag = True
        form.helper.add_input(Submit('submit', 'Continue'))
        
        return form

    def form_valid(self, form):
        
        trips_year = TripsYear.objects.current()
        form.instance.applicant = self.request.user
        form.instance.trips_year = trips_year
        # form.status??
        application = form.save()

        # create blank croo and leader supplements for the application
        LeaderSupplement.objects.create(trips_year=trips_year, application=application)
        CrooSupplement.objects.create(trips_year=trips_year, application=application)

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        trips_year=TripsYear.objects.current()
        return super(NewApplication, self).get_context_data(
            trips_year=trips_year,
            timetable=Timetable.objects.timetable(),
            information=ApplicationInformation.objects.get(trips_year=trips_year),
            **kwargs
        )


class ApplicationBaseUpdateView(FormMessagesMixin, MultipleFormMixin, 
                                CrispyFormMixin, UpdateView):
    """ 
    Base view to edit applications.

    Used by the public facing application, as well as the backend database view
    """
    model = GeneralApplication
    template_name = 'applications/continue_application.html'
    success_url = reverse_lazy('applications:continue')
    context_object_name = 'application'

    form_valid_message = "Your application has been saved"
    form_invalid_message = "Uh oh. Looks like there's a problem somewhere in your application"
    
    def get_object(self):
        return get_object_or_404(self.model, 
                                 applicant=self.request.user,
                                 trips_year=TripsYear.objects.current())

    def get_instances(self):

        self.object = self.get_object()
        return {
            'form': self.object,
            'leader_form': self.object.leader_supplement,
            'croo_form': self.object.croo_supplement,
        }

    def get_form_classes(self):

        return {
            'form': ApplicationForm,
            'leader_form': LeaderSupplementForm,
            'croo_form': CrooSupplementForm,
        }

    def get_context_data(self, **kwargs):
        context = super(ApplicationBaseUpdateView, self).get_context_data(**kwargs)
        trips_year = TripsYear.objects.current()
        context['timetable'] = Timetable.objects.timetable()
        context['information'] = ApplicationInformation.objects.get(trips_year=trips_year)
        context['triptypes'] = TripType.objects.filter(trips_year=trips_year)
        context['trips_year'] = trips_year
        return context


class ContinueApplication(LoginRequiredMixin, IfApplicationAvailable,  
                          ApplicationBaseUpdateView):
    """ Protect the ApplicationBaseView logic with login """
    pass


class SetupApplication(CreateApplicationsPermissionRequired, 
                       CrispyFormMixin, UpdateView):
    """
    Create/edit this year's application

    Used by directors to edit application questions, general information.

    TOOD: show previous year's application documents??? 
    """

    model = ApplicationInformation
    template_name = 'applications/setup.html'
    success_url = reverse_lazy('applications:setup')

    def get_object(self):
        """ There is only one configuration object for each trips year. """
        trips_year = TripsYear.objects.current()
        obj, created = self.model.objects.get_or_create(trips_year=trips_year)
        
        return obj

    def get_form(self, **kwargs):

        form = super(SetupApplication, self).get_form(**kwargs)
        form.helper = FormHelper(form)
        form.helper.add_input(Submit('submit', 'Update'))

        return form

    def get_context_data(self, **kwargs):
        """ Add current tripsyear to template context """
        context = super(SetupApplication, self).get_context_data(**kwargs)
        context['trips_year'] = TripsYear.objects.current()
        return context


class ApplicationDatabaseListView(DatabaseListView):
    model = GeneralApplication
    context_object_name = 'applications'
    template_name = 'applications/application_index.html'


class LeaderApplicationDatabaseListView(DatabaseListView):
    model = LeaderSupplement
    context_object_name = 'applications'
    template_name = 'applications/leaderapplication_index.html'

    def get_queryset(self):
        return self.model.objects.completed_applications(self.kwargs['trips_year'])


class LeaderApplicationDatabaseDetailView(DatabaseDetailView):
    model = LeaderSupplement
    template_name = 'applications/leaderapplication_detail.html'
    fields = ('trip_preference_comments', 'cannot_participate_in')


class LeaderApplicationDatabaseUpdateView(DatabaseMixin, ApplicationBaseUpdateView):
    template_name = 'applications/leaderapplication_update.html'


class LeaderApplicationAdminDatabaseUpdateView(DatabaseUpdateView):
    """ Edit admin data - trainings, application status """
    model = LeaderSupplement
    form_class = LeaderSupplementAdminForm
    template_name = 'applications/leaderapplication_admin_update.html'
    
        
        
        
## --------- grading views ----------------


class RedirectToNextGradableCrooApplication(CrooGraderPermissionRequired, 
                                            RedirectView):
    """ 
    Grading portal, redirects to next app to grade. 
    Identical to the corresponding LeaderGrade view 

    Restricted to directorate members.
    """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        """ Redirect to next CrooApplication which needs grading """
        
        application = CrooSupplement.objects.next_to_grade(self.request.user)
        if not application:
            return reverse('applications:grade:no_croo_left')
        return reverse('applications:grade:croo', kwargs={'pk': application.pk})


class GradeCrooApplication(CrooGraderPermissionRequired, CreateView):

    model = CrooApplicationGrade
    form_class = CrooApplicationGradeForm
    template_name = 'applications/grade.html'

    success_url = reverse_lazy('applications:grade:next_croo')

    def get_context_data(self, **kwargs):
        
        context = super(GradeCrooApplication, self).get_context_data(**kwargs)
        # only grade applications from this year
        context['application'] = get_object_or_404(CrooSupplement, 
                                                   trips_year=TripsYear.objects.current())
        return context

    def form_valid(self, form):
        
        form.instance.grader = self.request.user
        form.instance.application = get_object_or_404(CrooSupplement,
                                                      trips_year=TripsYear.objects.current())
        form.save()
        
        return super(GradeCrooApplication, self).form_valid(form)
        
    
class NoCrooApplicationsLeftToGrade(CrooGraderPermissionRequired, TemplateView):
    
    template_name = 'applications/no_applications.html'
    

    

    
        
        
