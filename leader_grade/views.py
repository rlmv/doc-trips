
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic.edit import CreateView, FormView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.db.models import Count
from django.forms import ModelForm

from .models import LeaderGrade
from leader.models import LeaderApplication
from leader.views import LeaderApplicationView

import logging
logger = logging.getLogger(__name__)

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
           .annotate(Count('leadergrade'))
           .filter(leadergrade__count=num)
           .exclude(leadergrade__grader=user)
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
    return redirect('grade:grade', pk=application.pk)
    

class LeaderGradeForm(ModelForm):
    class Meta:
        model = LeaderGrade
        fields = ['grade', 'comment', 'hard_skills', 'soft_skills']

class GradeApplicationView(FormView, LeaderApplicationView):

    template_name = 'leader_grade/grade.html'

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






