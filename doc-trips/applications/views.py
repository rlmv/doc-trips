
from vanilla import CreateView, UpdateView
from braces.views import LoginRequiredMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from db.views import CrispyFormMixin
from db.models import TripsYear
from timetable.models import Timetable
from applications.models import GeneralApplication


class NewApplication(LoginRequiredMixin, CrispyFormMixin, CreateView):

    model = GeneralApplication
    template_name = 'applications/new_application.html'
    success_url = reverse_lazy('applications:continue')

    def dispatch(self, request, *args, **kwargs):
        """ If user has already applied, redirect to edit existing application """

        if self.models.objects.filter(applicant=self.request.user, 
                                      trips_year=TripsYear.objects.current()).exists():
            return HttpResponseRedirect(self.get_success_url())

        return super(NewApplication, self).dispatch(request, *args, **kwargs)

    def get_form_helper(self, form):
        # layout = GeneralApplicationLayout
        helper = FormHelper(form)
        helper.add_input(Submit('submit', 'Continue'))
        return helper

    def form_valid(self, form):
        
        form.instance.applicant = self.request.user
        form.instance.trips_year = TripsYear.objects.current()
        # form.status??
        form.save()

        return HttpResponseRedirect(self.get_success_url())


class ContinueApplication(LoginRequiredMixin, CrispyFormMixin, UpdateView):

    model = GeneralApplication
    template_name = 'applications/continue_application.html'
    success_url = reverse_lazy('applications:continue')
    
    def get_object(self):
        return get_object_or_404(self.model, 
                                 applicant=self.request.user, 
                                 trips_year=TripsYear.objects.current())

    
    def get(self, request, *args, **kwargs):
        
        self.object = self.get_object()
        form = self.get_form(instance=self.object)
        # pass instance args??
        leader_form = self.get_leader_form()
        croo_form = self.get_croo_form()

        context = get_context_data(form=form, leader_form=leader_form, 
                                   croo_form=croo_form)
        return self.render_to_response(context)

    def post(self, request, **args, **kwargs):
        
        self.object = self.get_object()
        form = self.get_form(data=request.POST, instance=self.object)
        croo_form = self.get_croo_form(data=request.POST, files=request.FILES)
        leader_form = self.get_leader_form(data=request.POST, files=request.FILES)

        if all(form.is_valid(), leader_form.is_valid(), croo_form.is_valid()):
            return self.form_valid(form, croo_form, leader_form)

        return self.form_invalid(form, croo_form, leader_form)
            
    def get_leader_form(self, data=None, files=None):
        pass

    def get_croo_form(self, data=None, files=None):
        pass

    def form_valid(self, form, croo_form, leader_form):

        form.save()
        croo_form.save()
        leader_form.save()
        
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, croo_form, leader_form):
        
        msg = "Uh oh. Looks like there's a problem somewhere in your application"
        messages.error(self.request, msg)
        
        context = self.get_context_data(form=form, croo_form=croo_form, 
                                        leader_form=leader_form)
        return self.render_to_response(context)
        
    def get_context_data(self, **kwargs):
        context = super(ContinueApplication, self).get_context_data(**kwargs)
        context['timetable'] = Timetable.objects.timetable()
        return context
        
        
        
