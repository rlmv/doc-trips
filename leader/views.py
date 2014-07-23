
from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.views.generic.base import RedirectView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.db.models import Count
from django.forms import ModelForm

from constance import config

from .models import LeaderApplication, LeaderGrade

import logging
logger = logging.getLogger(__name__)

from django_easyfilters import FilterSet
class LeaderApplicationFilterSet(FilterSet):
    fields = [
        'status',
        'class_year',
    ]

from vanilla import ListView

class FilterListView(ListView):

    """ Implements easyfilter filtering on a vanilla ListView. 

    filterset and context_filter_name attributes must be specified.
    """
    
    filterset = None # filterset object
    context_filter_name = None # context name of filter
    
    def __init__(self, *args, **kwargs):
        super(FilterListView, self).__init__(*args, **kwargs)
        
        if self.filterset is None or self.context_filter_name is None:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured("FilterListView requires 'filterset' "
                                       "and 'context_filter_name' attributes")
    
    def get_queryset(self):
        qs = super(FilterListView, self).get_queryset()
        self.filter_object = self.filterset(qs, self.request.GET)
        return self.filter_object.qs

    def get_context_data(self, **kwargs):
        context = super(FilterListView, self).get_context_data(**kwargs)
        context[self.context_filter_name] = self.filter_object
        return context

        
class LeaderApplicationList(FilterListView):
    
    model = LeaderApplication
    template_name = 'leader/list_application.html'
    context_object_name = 'applications'
    filterset = LeaderApplicationFilterSet
    context_filter_name = 'application_filter'

list_view = login_required(LeaderApplicationList.as_view())
    

class LeaderApplicationView(DetailView):
    model = LeaderApplication
    context_object_name = 'leader_application'
    # default template : leaderapplication_detail.html
    
leaderapplication = login_required(LeaderApplicationView.as_view())

class CreateLeaderApplication(CreateView):
    model = LeaderApplication
    fields = ['class_year', 'gender', 'tshirt_size', 'hinman_box', 'phone',
              'offcampus_address', 'notes',] 
    
    def form_valid(self, form):
        """ Attach creating user to Application. """
        form.instance.user = self.request.user
        return super(CreateLeaderApplication, self).form_valid(form)

    # the views uses the default form leaderapplication_form.html

create_leaderapplication = login_required(CreateLeaderApplication.as_view())

class EditLeaderApplication(UpdateView):
    model = LeaderApplication
    fields = '__all__'

edit_leaderapplication = login_required(EditLeaderApplication.as_view())



def get_next_application_to_grade(user):
    """ Find the next leader application to grade.

    This is an application which meets the following conditions:
    (1) has not yet been graded if there are apps in the database
    which have not been graded, otherwise an application with only 
    one grade.
    (2) has not already been graded by this user
    (3) the application is not disqualified, deprecated, etc. See
    LeaderApplication status field.

    """

    app = get_random_application_by_num_grades(user, 0)
    if not app:
        app = get_random_application_by_num_grades(user, 1)

    return app

def get_random_application_by_num_grades(user, num):

    app = (LeaderApplication.objects
           .annotate(Count('grades'))
           .filter(grades__count=num)
           .exclude(grades__grader=user)
           # random ordering. TODO: this may be expensive?
           .order_by('?')[:1])
    
    return app[0] if app else None


# TODO: needs to be grader permission based
# TODO: convert to class view
@login_required
def redirect_to_next_gradable_application(request):

    application = get_next_application_to_grade(request.user)
    # TODO: use template
    if not application:
        return HttpResponse('<h3>No applications left to grade </h3>')
    return redirect('leader:grade', pk=application.pk)
    

class LeaderGradeForm(ModelForm):
    class Meta:
        model = LeaderGrade
        fields = ['grade', 'comment', 'hard_skills', 'soft_skills']


# TODO: refactor this using vanilla views
class GradeApplicationView(FormView, LeaderApplicationView):

    template_name = 'leader/grade.html'

    # form parameters
    form_class = LeaderGradeForm
    """ The form is passed to the template as 'form' for compatibilty
    with FormView.form_invalid. """

    """ Must be a lazy - this is called before the urlconf is loaded.
    See http://stackoverflow.com/a/22903110/3818777 """
    success_url = reverse_lazy('grade:random')
    
    def form_valid(self, form):
        """ Add grader and application to the grade, save to database.
        
        Redirects to success_url. 
        """
        
        grade = form.save(commit=False)
        grade.grader = self.request.user
        grade.leader_application = self.get_object()
        grade.save()

        return super(GradeApplicationView, self).form_valid(form)

    def get_context_data(self, form=None, **kwargs):
        """ Override the FormView and ApplicationView context data.

        Necessary to send both form and object to the template. """
        
        context = {}
        
        obj = self.get_object()
        context[self.get_context_object_name(obj)] = obj
        if not form:
            form = self.get_form(self.get_form_class())
        context['form'] = form

        context.update(**kwargs)
        
        return context
    
grade_application = GradeApplicationView.as_view()    






