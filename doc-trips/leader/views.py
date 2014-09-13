
import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponse
from django.db.models import Count
from django.forms import ModelForm
from django import forms

from vanilla import (ListView, CreateView, DetailView, UpdateView, 
                     FormView, RedirectView, TemplateView)

from permissions.views import GraderPermissionRequired, LoginRequiredMixin

from leader.models import LeaderApplication, LeaderGrade
from db.views import *
from db.models import TripsYear
from db.forms import tripsyear_modelform_factory
from timetable.models import Timetable

logger = logging.getLogger(__name__)


class LeaderApplicationDatabaseListView(DatabaseListView):
    model = LeaderApplication
    context_object_name = 'leaderapplications'
    template_name = 'leader/leaderapplication_index.html'


class LeaderApplicationDatabaseUpdateView(DatabaseUpdateView):
    model = LeaderApplication
    # custom template to handle trip assignment
    template_name = 'leader/db_application_update.html'


class LeaderApply(LoginRequiredMixin, UpdateView):

    model = LeaderApplication
    success_url = reverse_lazy('leader:apply')

    exclude = ['user', 'status', 'assigned_trip']

    def get_template_names(self):
        """
        Only display the application form if the application is open.

        """
        if Timetable.objects.timetable().is_leader_application_available():
            return ['leader/application_form.html']
        else:
            return ['leader/application_not_available.html']

    def get_object(self):
        """ 
        Return the application for this user.

        If the user has already applied this year, display a form for them to
        edit. Otherwise, display an empty application form. 
        """
        try:
            return self.get_queryset().get(user=self.request.user, 
                                        trips_year=TripsYear.objects.current())
        except self.model.DoesNotExist:
            return None # causes self.object and context[object] to be None

    def get_form_class(self):
        """ Get form, restricting section choices to those of current TripsYear """
        form =  tripsyear_modelform_factory(self.model, TripsYear.objects.current(),
                                            exclude=self.exclude)
        
        from leader.forms import LeaderApplicationFormHelper
        from crispy_forms.layout import Submit
        form.helper = LeaderApplicationFormHelper()
        if self.object:
            submit_text = 'Update'
        else:
            submit_text = 'Submit'
        form.helper.add_input(Submit('submit', submit_text))
        return form

    def form_valid(self, form):
        """ Attach creating user and current trips_year to Application. """
        if self.object is None:
            form.instance.user = self.request.user
            form.instance.trips_year = TripsYear.objects.current()
        return super(LeaderApply, self).form_valid(form)
        

class RedirectToNextGradableApplication(GraderPermissionRequired, RedirectView):
    
    # from RedirectView
    permanent = False 
    
    def get_redirect_url(self, *args, **kwargs):
        """ Return the url of the next LeaderApplication that needs grading """
        
        application = LeaderApplication.objects.next_to_grade(self.request.user)
        if not application:
            return reverse('leader:no_application')
        return reverse('leader:grade', kwargs={'pk': application.pk})


class NoApplicationToGrade(GraderPermissionRequired, TemplateView):
    """ Tell user there are no more applications for her to grade """

    template_name = 'leader/no_application.html'


class LeaderGradeForm(ModelForm):
    class Meta:
        model = LeaderGrade
        fields = ['grade', 'comment', 'hard_skills', 'soft_skills']


# TODO: restrict this to those with grader permissions
class GradeApplication(GraderPermissionRequired, DetailView, FormView):

    """ Grade a LeaderApplication object. 

    The DetailView encapsulates the LeaderApplication, 
    the FormView the grade form. 
    """

    model = LeaderApplication
    template_name = 'leader/grade.html'
    context_object_name = 'leaderapplication'

    form_class = LeaderGradeForm
    success_url = reverse_lazy('leader:grade_random')

    def get_context_data(self, **kwargs):
        """ Get context data to render in template.

        Because The DetailView is first in the MRO inheritance tree,
        The super call retrives the LeaderApplication object (saved as context_object      
        Then we manually add the form instance.
        """
        context = super(GradeApplication, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context
    
    def form_valid(self, form):
        """ Attach grader and application to the grade, save grade to database.
        
        Redirects to success_url. 
        """
        grade = form.save(commit=False)
        grade.grader = self.request.user
        grade.leader_application = self.get_object()
        grade.trips_year = TripsYear.objects.current()
        grade.save()

        return super(GradeApplication, self).form_valid(form)






