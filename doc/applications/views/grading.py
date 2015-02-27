
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


class GradeCrooApplication(CrooGraderPermissionRequired, 
                           IfGradingAvailable, CreateView):

    model = CrooApplicationGrade
    form_class = CrooApplicationGradeForm
    template_name = 'applications/grade.html'

    success_url = reverse_lazy('applications:grade:next_croo')

    def get_application(self):
        return get_object_or_404(CrooSupplement, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        
        context = super(GradeCrooApplication, self).get_context_data(**kwargs)
        context['application'] = self.get_application()
        context['title'] = 'Grade Croo Application #%s' % self.kwargs['pk']

        return context

    def form_valid(self, form):
        
        form.instance.grader = self.request.user
        form.instance.application = self.get_application()
        form.save()
        
        return super(GradeCrooApplication, self).form_valid(form)
        
    
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


class GradeLeaderApplication(LeaderGraderPermissionRequired, 
                             IfGradingAvailable, CreateView):

    model = LeaderApplicationGrade
    form_class = LeaderApplicationGradeForm
    template_name = 'applications/grade.html'

    success_url = reverse_lazy('applications:grade:next_leader')

    def get_application(self):
        return get_object_or_404(LeaderSupplement, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        
        context = super(GradeLeaderApplication, self).get_context_data(**kwargs)
        context['application'] = self.get_application()
        context['title'] = 'Grade Trip Leader Application #%s' % self.kwargs['pk']
        return context

    def form_valid(self, form):
        
        form.instance.grader = self.request.user
        form.instance.application = self.get_application()
        form.save()
        
        return super(GradeLeaderApplication, self).form_valid(form)


class NoLeaderApplicationsLeftToGrade(LeaderGraderPermissionRequired, 
                                      IfGradingAvailable, TemplateView):
    """ Tell user there are no more applications for her to grade """

    template_name = 'applications/no_applications.html'

        
