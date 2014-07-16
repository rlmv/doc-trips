
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.db.models import Count

from .models import LeaderGrade
from leader.models import LeaderApplication

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
@login_required
def redirect_to_next_gradable_application(request):

    application = get_next_application_to_grade(request.user)
    # TODO: use template
    if not application:
        return HttpResponse('<h3>No applications left to grade </h3>')
    logger.debug(application.hinman_box)
    return redirect('grade:grade', pk=application.pk)
    

class GradeApplicationView(DetailView):
    # TODO: POST to this view should create a grade

    model = LeaderApplication
    template_name = 'leader_grade/grade.html'
    context_object_name = 'leader_application'
    
grade_application = GradeApplicationView.as_view()    






