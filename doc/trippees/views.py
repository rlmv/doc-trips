

from django import forms
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from vanilla import CreateView, UpdateView, DetailView, TemplateView, ListView, FormView
from braces.views import LoginRequiredMixin

from doc.trippees.models import TrippeeRegistration, Trippee
from doc.trippees.forms import RegistrationForm
from doc.db.models import TripsYear
from doc.db.views import TripsYearMixin
from doc.timetable.models import Timetable
from doc.permissions.views import (DatabaseReadPermissionRequired,
                                   DatabaseEditPermissionRequired)

class IfRegistrationAvailable():
    """ Redirect if trippee registration is not currently available """

    def dispatch(self, request, *args, **kwargs):
        
        if not Timetable.objects.timetable().registration_available():
            return HttpResponseRedirect(reverse('trippees:registration_not_available'))
        return super(IfRegistrationAvailable, self).dispatch(request, *args, **kwargs)


class RegistrationNotAvailable(TemplateView):
    template_name = 'trippees/not_available.html'


class Register(LoginRequiredMixin, IfRegistrationAvailable, CreateView):
    """ 
    Register for trips 
    """
    model = TrippeeRegistration
    template_name = 'trippees/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('trippees:view_registration')

    def form_valid(self, form, **kwargs):
        """ 
        Add the registering user to the registration 

        The registration will be automagically matched with a 
        corresponding Trippee model if it exists.
        """

        form.instance.trips_year = TripsYear.objects.current()
        form.instance.user = self.request.user
        return super(Register, self).form_valid(form, **kwargs)


class EditRegistration(LoginRequiredMixin, IfRegistrationAvailable, UpdateView):
    """
    Edit a trippee registration.
    """
    model = TrippeeRegistration
    template_name = 'trippees/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('trippees:view_registration')

    def get_object(self):
        """ Get registration for user """        
        return get_object_or_404(
            self.model, user=self.request.user,
            trips_year=TripsYear.objects.current()
        )
           
 
class ViewRegistration(LoginRequiredMixin, IfRegistrationAvailable, DetailView):
    """
    View a complete registration 
    """
    model = TrippeeRegistration
    template_name = 'trippees/completed_registration.html'
    fields = ['name'] # TODO
    
    def get_object(self):
        """ Get registration for user """
        return get_object_or_404(
            self.model, user=self.request.user,
            trips_year=TripsYear.objects.current()
        )
           
         

class RegistrationIndexView(DatabaseReadPermissionRequired, 
                            TripsYearMixin, ListView):
    
    model = TrippeeRegistration
    template_name = 'trippees/registration_index.html'

    
class TrippeeIndexView(DatabaseReadPermissionRequired,
                       TripsYearMixin, ListView):
    
    model = Trippee
    template_name = 'trippees/trippee_index.html'


class IncomingStudentsForm(forms.Form):

    csv_file = forms.FileField()
    

class UploadIncomingStudentData(DatabaseEditPermissionRequired,
                                TripsYearMixin, FormView):
    """
    Accept an upload of CSV file of incoming students. 

    Parses the CSV file and adds the data to the database as
    CollegeInfo objects.
    """

    form_class = IncomingStudentsForm
    template_name = 'trippees/upload_incoming_students.html'
    
    
    
 

    
