
from vanilla import CreateView, UpdateView
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib import messages

from db.views import CrispyFormMixin
from db.models import TripsYear
from db.forms import tripsyear_modelform_factory
from timetable.models import Timetable
from trips.models import TripType
from applications.models import GeneralApplication, LeaderSupplement, CrooSupplement, ApplicationInformation
from applications.forms import ApplicationForm, CrooSupplementForm, LeaderSupplementForm

class IfApplicationsAvailable():

    def dispatch(self, request, *args, **kwargs):
        if Timetable.objects.timetable().applications_available():
            return super(IfApplicationsAvailable, self).dispatch(request, *args, **kwargs)
        
        return render(request, 'applications/not_available.html')


class NewApplication(LoginRequiredMixin, IfApplicationsAvailable, 
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
        


class ContinueApplication(LoginRequiredMixin, IfApplicationsAvailable, 
                          CrispyFormMixin, UpdateView):

    model = GeneralApplication
    template_name = 'applications/continue_application.html'
    success_url = reverse_lazy('applications:continue')
    context_object_name = 'application'
    
    def get_object(self):
        return get_object_or_404(self.model, 
                                 applicant=self.request.user,
                                 trips_year=TripsYear.objects.current())
    
    def get(self, request, *args, **kwargs):
        
        self.object = self.get_object()
        form = self.get_form(instance=self.object)
        croo_form = self.get_croo_form(instance=self.object.croo_supplement)
        leader_form = self.get_leader_form(instance=self.object.leader_supplement)

        context = self.get_context_data(form=form, leader_form=leader_form, 
                                   croo_form=croo_form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs): 
        
        self.object = self.get_object()
        form = self.get_form(data=request.POST, instance=self.object)
        croo_form = self.get_croo_form(data=request.POST, 
                                       files=request.FILES,
                                       instance=self.object.croo_supplement)
        leader_form = self.get_leader_form(data=request.POST, 
                                           files=request.FILES, 
                                           instance=self.object.leader_supplement)

        valid = map(lambda x: x.is_valid(), [form, leader_form, croo_form])
        if all(valid):
            return self.form_valid(form, croo_form, leader_form)

        return self.form_invalid(form, croo_form, leader_form)

    def get_form(self, **kwargs):
        
        return ApplicationForm(**kwargs)

    def get_leader_form(self, **kwargs):
        
        return LeaderSupplementForm(**kwargs)

    def get_croo_form(self, **kwargs):
        
        return CrooSupplementForm(**kwargs)

    def form_valid(self, form, croo_form, leader_form):

        form.save()
        croo_form.save()
        leader_form.save()

        msg = "Your application has been saved"
        messages.success(self.request, msg)
        
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, croo_form, leader_form):
        
        msg = "Uh oh. Looks like there's a problem somewhere in your application"
        messages.error(self.request, msg)
        
        context = self.get_context_data(form=form, croo_form=croo_form, 
                                        leader_form=leader_form)
        return self.render_to_response(context)
        
    def get_context_data(self, **kwargs):
        context = super(ContinueApplication, self).get_context_data(**kwargs)
        trips_year = TripsYear.objects.current()
        context['timetable'] = Timetable.objects.timetable()
        context['information'] = ApplicationInformation.objects.get(trips_year=trips_year)
        context['triptypes'] = TripType.objects.filter(trips_year=trips_year)
        context['trips_year'] = trips_year
        return context
        

class SetupApplication(LoginRequiredMixin, PermissionRequiredMixin, CrispyFormMixin, UpdateView):
    """
    Create/edit this year's application

    Used by directors to edit application questions, general information.

    TOOD: show previous year's application documents??? 
    """

    model = ApplicationInformation
    template_name = 'applications/setup.html'
    success_url = reverse_lazy('applications:setup')

    # user must have permission to change application
    permission_required = 'can_create_applications'
    redirect_unauthenticated_users = True
    raise_exception = True

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
        
        
        
    
    

    

    
        
        
