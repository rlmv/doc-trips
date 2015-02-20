
from vanilla import RedirectView, TemplateView, CreateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render

from db.models import TripsYear
from applications.models import GeneralApplication, LeaderSupplement, CrooSupplement, CrooApplicationGrade, LeaderApplicationGrade
from applications.forms import CrooApplicationGradeForm
from permissions.views import CrooGraderPermissionRequired

        
class RedirectToNextGradableCrooApplication(CrooGraderPermissionRequired, 
                                            RedirectView):
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


class GradeCrooApplication(CrooGraderPermissionRequired, CreateView):

    model = CrooApplicationGrade
    form_class = CrooApplicationGradeForm
    template_name = 'applications/grade.html'

    success_url = reverse_lazy('applications:grade:next_croo')

    def get_context_data(self, **kwargs):
        
        context = super(GradeCrooApplication, self).get_context_data(**kwargs)
        # only grade applications from this year
        context['application'] = get_object_or_404(CrooSupplement, 
                                                   trips_year=TripsYear.objects.current())
        return context

    def form_valid(self, form):
        
        form.instance.grader = self.request.user
        form.instance.application = get_object_or_404(CrooSupplement,
                                                      trips_year=TripsYear.objects.current())
        form.save()
        
        return super(GradeCrooApplication, self).form_valid(form)
        
    
class NoCrooApplicationsLeftToGrade(CrooGraderPermissionRequired, TemplateView):
    
    template_name = 'applications/no_applications.html'
    

    

    
        
        
