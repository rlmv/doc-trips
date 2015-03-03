
from braces.views import FormMessagesMixin
from vanilla import RedirectView, TemplateView, CreateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render

from doc.db.models import TripsYear
from doc.applications.models import GeneralApplication, LeaderSupplement, CrooSupplement, CrooApplicationGrade, LeaderApplicationGrade
from doc.applications.forms import CrooApplicationGradeForm, LeaderApplicationGradeForm
from doc.permissions.views import (CrooGraderPermissionRequired, 
                               LeaderGraderPermissionRequired)
from doc.timetable.models import Timetable


class IfGradingAvailable():
    
    """ Only allow grading once applications are closed """

    def dispatch(self, request, *args, **kwargs):
        if Timetable.objects.timetable().grading_available():
            return super(IfGradingAvailable, self).dispatch(request, *args, **kwargs)

        return render(request, 'applications/grading_not_available.html')


class GenericGradingView(IfGradingAvailable, FormMessagesMixin, CreateView):
    """ 
    Shared logic for grading Croo and Leader applications.
    """

    model = None
    application_model = None
    form_class = None
    success_url = None
    verbose_application_name = None # eg. Trip Leader Application
    template_name = 'applications/grade.html'
    form_invalid_message = 'Uh oh, looks like you forgot to fill out a field'

    def get_application(self):
        return get_object_or_404(self.application_model, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
         
        context = super(GenericGradingView, self).get_context_data(**kwargs)
        context['application'] = self.get_application()
        context['title'] = 'Grade %s #%s' % (self.verbose_application_name, self.kwargs['pk'])
        context['score_choices'] = map(lambda c: c[1], self.model.SCORE_CHOICES)
        return context

    def form_valid(self, form):
        
        form.instance.grader = self.request.user
        form.instance.application = self.get_application()
        form.save()
        
        return super(GenericGradingView, self).form_valid(form)


class GraderLandingPage(TemplateView):

    template_name = 'applications/graders.html'


class RedirectToNextGradableCrooApplication(CrooGraderPermissionRequired, 
                                            IfGradingAvailable, RedirectView):
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


class GradeCrooApplication(CrooGraderPermissionRequired, GenericGradingView):

    model = CrooApplicationGrade
    application_model = CrooSupplement
    form_class = CrooApplicationGradeForm
    success_url = reverse_lazy('applications:grade:next_croo')
    verbose_application_name = 'Croo Application'
        
    
class NoCrooApplicationsLeftToGrade(CrooGraderPermissionRequired, 
                                    IfGradingAvailable, TemplateView):
    
    template_name = 'applications/no_applications.html'
    

class RedirectToNextGradableLeaderApplication(LeaderGraderPermissionRequired, 
                                              IfGradingAvailable, RedirectView):
    
    # from RedirectView
    permanent = False 
    
    def get_redirect_url(self, *args, **kwargs):
        """ Return the url of the next LeaderApplication that needs grading """
        
        application = LeaderSupplement.objects.next_to_grade(self.request.user)
        if not application:
            return reverse('applications:grade:no_leaders_left')
        return reverse('applications:grade:leader', kwargs={'pk': application.pk})


class GradeLeaderApplication(LeaderGraderPermissionRequired, GenericGradingView):

    model = LeaderApplicationGrade
    application_model = LeaderSupplement
    form_class = LeaderApplicationGradeForm
    success_url = reverse_lazy('applications:grade:next_leader')
    verbose_application_name = 'Trip Leader Application'


class NoLeaderApplicationsLeftToGrade(LeaderGraderPermissionRequired, 
                                      IfGradingAvailable, TemplateView):
    """ Tell user there are no more applications for her to grade """

    template_name = 'applications/no_applications.html'

        
