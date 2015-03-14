import io
import logging

from django import forms
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from vanilla import CreateView, UpdateView, DetailView, TemplateView, ListView, FormView
from braces.views import LoginRequiredMixin

from doc.trippees.models import Registration, IncomingStudent
from doc.trippees.forms import RegistrationForm, IncomingStudentsForm
from doc.db.models import TripsYear
from doc.db.views import TripsYearMixin
from doc.timetable.models import Timetable
from doc.permissions.views import (DatabaseReadPermissionRequired,
                                   DatabaseEditPermissionRequired)

""" 
Views for incoming students.

The first set of views are public facing and allow incoming 
students to register for trips. The second set handle manipulation of
registrations and trippees in the database.

"""

logger = logging.getLogger(__name__)


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
    model = Registration
    template_name = 'trippees/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('trippees:view_registration')

    def form_valid(self, form, **kwargs):
        """ 
        Add the registering user to the registration 

        The registration will be automagically matched with a 
        corresponding IncomingStudent model if it exists.
        """
        form.instance.trips_year = TripsYear.objects.current()
        form.instance.user = self.request.user
        return super(Register, self).form_valid(form, **kwargs)


class EditRegistration(LoginRequiredMixin, IfRegistrationAvailable, UpdateView):
    """
    Edit a trippee registration.
    """
    model = Registration
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
    model = Registration
    template_name = 'trippees/completed_registration.html'
    fields = ['name'] # TODO
    
    def get_object(self):
        """ Get registration for user """
        return get_object_or_404(
            self.model, user=self.request.user,
            trips_year=TripsYear.objects.current()
        )
           

# ----- database internal views --------

class RegistrationIndexView(DatabaseReadPermissionRequired, 
                            TripsYearMixin, ListView):
    """ All trippee registrations """

    model = Registration
    template_name = 'trippees/registration_index.html'
    context_object_name = 'registrations'

    
class IncomingStudentIndexView(DatabaseReadPermissionRequired,
                               TripsYearMixin, ListView):
    """ All incoming students """

    model = IncomingStudent
    template_name = 'trippees/trippee_index.html'
    context_object_name = 'trippees'


class IncomingStudentDetailView(DatabaseReadPermissionRequired,
                                TripsYearMixin, DetailView):
    model = IncomingStudent
    template_name = 'trippees/trippee_detail.html'
    context_object_name = 'trippee'

    admin_fields = ['registration', 'trip_assignment', 
                    'decline_reason', 'notes']
    college_fields = ['name', 'netid', 'class_year', 'gender',
                      'ethnic_code', 'incoming_status', 'email', 
                      'blitz']


class IncomingStudentUpdateView(DatabaseEditPermissionRequired,
                                TripsYearMixin, UpdateView):
    model = IncomingStudent
    template_name = 'db/update.html'
    context_object_name = 'trippee'
    

class UploadIncomingStudentData(DatabaseEditPermissionRequired,
                                TripsYearMixin, FormView):
    """
    Accept an upload of CSV file of incoming students. 

    Parses the CSV file and adds the data to the database as
    CollegeInfo objects.

    TODO: parse or input the status of the incoming student 
    (eg first year, transfer, etc.)
    """

    form_class = IncomingStudentsForm
    template_name = 'trippees/upload_incoming_students.html'

    def form_valid(self, form):

        file = io.TextIOWrapper(form.files['csv_file'].file, 
                                encoding='utf-8', errors='replace')

        (created, ignored) = IncomingStudent.objects.create_from_csv_file(file, self.kwargs['trips_year'])

        msg = 'Created incoming students with NetIds %s' % created
        logger.info(msg)
        messages.info(self.request, msg)
        
        msg = 'Ignored existing incoming students with NetIds %s' % ignored
        logger.info(msg)
        messages.warning(self.request, msg)

        return super(UploadIncomingStudentData, self).form_valid(form)        

    def get_success_url(self):
        return self.request.path
        
 

    
