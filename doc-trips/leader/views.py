
import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.db.models import Count
from django.forms import ModelForm

from vanilla import ListView, CreateView, DetailView, UpdateView, FormView, RedirectView
from django_easyfilters import FilterSet

from leader.models import LeaderApplication, LeaderGrade

from db.views import DatabaseViewFactory

logger = logging.getLogger(__name__)

class LeaderApplicationFilterSet(FilterSet):
    fields = [
        'status',
        'class_year',
    ]

# TODO: move this to a utils module
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

LeaderApplicationDatabaseViews = DatabaseViewFactory(LeaderApplication)


class CreateLeaderApplication(CreateView):
    model = LeaderApplication
    template_name = 'leader/application_form.html'
    fields = '__all__'

    def form_valid(self, form):
        """ Attach creating user to Application. """
        form.instance.user = self.request.user
        return super(CreateLeaderApplication, self).form_valid(form)

create_leaderapplication = login_required(CreateLeaderApplication.as_view())


class EditLeaderApplication(UpdateView):
    model = LeaderApplication
    template_name = 'leader/application_form.html'
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
    LeaderApplication status field. It should be PENDING.

    """

    app = get_random_application_by_num_grades(user, 0)
    if not app:
        app = get_random_application_by_num_grades(user, 1)

    return app

def get_random_application_by_num_grades(user, num):
    """ Return a random PENDING application that user has not graded, 
    which has only been graded by num people. """

    app = (LeaderApplication.objects
           .filter(status=LeaderApplication.PENDING)
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


class GradeApplicationView(DetailView, FormView):

    """ Grade a LeaderApplication object. 

    The DetailView encapsulates the LeaderApplication, 
    the FormView the grade form. 
    """

    model = LeaderApplication
    template_name = 'leader/grade.html'
    context_object_name = 'leader_application'

    form_class = LeaderGradeForm
    """ Must be a lazy - this is called before the urlconf is loaded.
    See http://stackoverflow.com/a/22903110/3818777 """
    success_url = reverse_lazy('leader:grade_random')

    def get_context_data(self, **kwargs):
        """ Get context data to render in template.

        Because The DetailView is first in the MRO inheritance tree,
        The super call retrives the LeaderaApplication object (saved as context_object_name).
        Then we manually add the form instance.
        """
        context = super(GradeApplicationView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context
    
    def form_valid(self, form):
        """ Attach grader and application to the grade, save grade to database.
        
        Redirects to success_url. 
        """
        grade = form.save(commit=False)
        grade.grader = self.request.user
        grade.leader_application = self.get_object()
        grade.save()

        return super(GradeApplicationView, self).form_valid(form)

# TODO: restrict to graders
grade_application = GradeApplicationView.as_view()    






