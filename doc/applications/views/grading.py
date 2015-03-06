
from braces.views import FormMessagesMixin
from vanilla import RedirectView, TemplateView, CreateView
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, ButtonHolder
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render
from django.contrib import messages

from doc.db.models import TripsYear
from doc.applications.models import GeneralApplication, LeaderSupplement, CrooSupplement, CrooApplicationGrade, LeaderApplicationGrade
from doc.applications.forms import CrooApplicationGradeForm, LeaderApplicationGradeForm
from doc.permissions.views import (CrooGraderPermissionRequired, 
                               LeaderGraderPermissionRequired)
from doc.timetable.models import Timetable
from doc.croos.models import Croo


class GraderLandingPage(TemplateView):

    template_name = 'applications/graders.html'
    
    def get_context_data(self, **kwargs):
        kwargs['croos'] = Croo.objects.filter(trips_year=TripsYear.objects.current())
        return super(GraderLandingPage, self).get_context_data(**kwargs)


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

    def get_form_valid_message(self):
        return 'Score submitted for {} #{}'.format(self.verbose_application_name,
                                                   self.kwargs['pk'])

    def get_application(self):
        return get_object_or_404(self.application_model, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
         
        context = super(GenericGradingView, self).get_context_data(**kwargs)
        context['application'] = self.get_application()
        context['title'] = 'Score %s #%s' % (self.verbose_application_name, self.kwargs['pk'])
        context['score_choices'] = map(lambda c: c[1], self.model.SCORE_CHOICES)
        return context

    def form_valid(self, form):
        
        form.instance.grader = self.request.user
        form.instance.application = self.get_application()
        form.save()
        
        return super(GenericGradingView, self).form_valid(form)

    def get_form(self, **kwargs):
        """ Add a Skip button to the form """
        form = super(GenericGradingView, self).get_form(**kwargs)
        form.helper = FormHelper(form)
        form.helper.layout.append(
            ButtonHolder(
                Submit('submit', 'Submit Score'),
                HTML('<a href="%s" class="btn btn-warning" role="button">Skip this Application</a>' % self.get_success_url()),
            )
        )
        return form


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


class RedirectToNextGradableCrooApplicationForCroo(RedirectToNextGradableCrooApplication):
    """ 
    View for returning croo-specific apps to grade. 

    Only redirects to apps which other graders have tagged with a specific 
    potential croo. This view is intended for Croo heads to use to do 
    once-over grading for all potential people on their croos. 
    """

    def get_redirect_url(self, *args, **kwargs):
        
        croo_pk = self.kwargs['croo_pk']
        croo = Croo.objects.get(pk=croo_pk)
        
        # we're just serving apps for the specified croo
        # and don't care about limits to the total number of grades
        # TODO: stick this on the manager?
        application = (CrooSupplement.objects
                       .completed_applications(trips_year=TripsYear.objects.current())
                       .filter(grades__potential_croos=croo_pk)
                       .filter(application__status=GeneralApplication.PENDING)
                       .exclude(grades__grader=self.request.user)
                       .order_by('?')[:1])
        msg = 'You are currently scoring potential %s applications' 
        messages.info(self.request, msg % croo)
        if not application: 
            return reverse('applications:grade:no_croo_left')
        return reverse('applications:grade:croo', kwargs={'pk': application.pk,
                                                          'croo_pk': croo_pk})

class GradeCrooApplication(CrooGraderPermissionRequired, GenericGradingView):

    model = CrooApplicationGrade
    application_model = CrooSupplement
    form_class = CrooApplicationGradeForm
    success_url = reverse_lazy('applications:grade:next_croo')
    verbose_application_name = 'Croo Application'

    def get_context_data(self, **kwargs):
        
        application = self.get_application()
        graders = list(map(lambda g: g.grader, application.grades.all()))
        kwargs['already_graded_by'] = graders
        return super(GradeCrooApplication, self).get_context_data(**kwargs)

    def get_success_url(self):

        name = 'applications:grade:next_croo'
        croo_pk = self.kwargs.get('croo_pk')
        if croo_pk:
            return reverse(name, kwargs=dict(croo_pk=croo_pk))
        return reverse(name)

    
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

        
