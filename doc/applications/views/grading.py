import logging

from braces.views import FormMessagesMixin
from vanilla import RedirectView, TemplateView, CreateView
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, ButtonHolder
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import HttpResponseRedirect

from doc.db.models import TripsYear
from doc.applications.models import (GeneralApplication, LeaderSupplement, CrooSupplement,
                                     CrooApplicationGrade, LeaderApplicationGrade,
                                     QualificationTag, 
                                     SkippedLeaderGrade, SkippedCrooGrade)
from doc.applications.forms import CrooApplicationGradeForm, LeaderApplicationGradeForm
from doc.permissions.views import (CrooGraderPermissionRequired, 
                               LeaderGraderPermissionRequired)
from doc.timetable.models import Timetable
from doc.croos.models import Croo


SHOW_GRADE_AVG_INTERVAL = 10
SKIP = 'skip'

logger = logging.getLogger(__name__)


class GraderLandingPage(TemplateView):

    template_name = 'applications/graders.html'
    
    def get_context_data(self, **kwargs):
        kwargs['qualifications'] = QualificationTag.objects.filter(trips_year=TripsYear.objects.current())
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
    skipped_grade_model = None
    form_class = None
    success_url = None
    verbose_application_name = None # eg. Trip Leader Application
    template_name = 'applications/grade.html'
    form_invalid_message = 'Uh oh, looks like you forgot to fill out a field'

    def get_form_valid_message(self):
        return 'Score submitted for {} #{}'.format(self.verbose_application_name,
                                                   self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        """ Check whether the grader is skipping this application """
        
        if SKIP in request.POST:
            logger.info('%s skipped %s %s' % (self.request.user, 
                                              self.verbose_application_name, 
                                              self.kwargs['pk']))
            return self.skip_application()

        return super(GenericGradingView, self).post(request, *args, **kwargs)


    def get_application(self):
        """ Return the Croo or Leader application to grade """

        return get_object_or_404(self.application_model, pk=self.kwargs['pk'])


    def skip_application(self):
        """ 
        Skip this application.

        Creates a skipped grade object so that this grader won't see
        this application again.
        """
        
        application = self.get_application()
        skip = self.skipped_grade_model.objects.create(
            trips_year=application.trips_year,
            application=application,
            grader=self.request.user,
        )
        return HttpResponseRedirect(self.get_success_url())


    def get_context_data(self, **kwargs):
        
        # Every SHOW_GRADE_AVG_INTERVAL tell the grader what their 
        # average grade has been (for this year, of course)
        ct = ContentType.objects.get_for_model(self.model)
        grades_by_user = (getattr(self.request.user, ct.model + 's')
                          .filter(trips_year=TripsYear.objects.current()))
        if (grades_by_user.count() % SHOW_GRADE_AVG_INTERVAL == 0 and 
                grades_by_user.count() != 0):
            avg_grade = grades_by_user.aggregate(models.Avg('grade'))['grade__avg']
            msg = ("Hey, just FYI your average awarded %s is %s. "
                   "We'll show you your average score every %s grades.")
            self.messages.info(msg % (self.model._meta.verbose_name, 
                                      avg_grade, SHOW_GRADE_AVG_INTERVAL))
            
        context = super(GenericGradingView, self).get_context_data(**kwargs)

        application = self.get_application()
        context['application'] = application
        context['title'] = 'Score %s #%s: NetId %s' % (self.verbose_application_name, self.kwargs['pk'], application.application.applicant.netid)
        context['score_choices'] = map(lambda c: c[1], self.model.SCORE_CHOICES)
        return context


    def form_valid(self, form):
        """ Add the grader and application to the grade """

        form.instance.grader = self.request.user
        form.instance.application = self.get_application()
        form.instance.trips_year = TripsYear.objects.current()
        form.save()
        
        return super(GenericGradingView, self).form_valid(form)


    def get_form(self, **kwargs):
        """ Add a Skip button to the form """

        form = super(GenericGradingView, self).get_form(**kwargs)
        form.helper = FormHelper(form)
        form.helper.layout.append(
            ButtonHolder(
                Submit('submit', 'Submit Score'),
                Submit('skip', 'Skip this Application', css_class='btn-warning'),
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


class RedirectToNextGradableCrooApplicationForQualification(CrooGraderPermissionRequired, 
                                                            IfGradingAvailable, RedirectView):
    """ 
    View for returning qualification-specific apps to grade. 

    Only redirects to apps which other graders have tagged with a specific 
    qualification. This view is intended for Croo heads to use to do 
    once-over grading for all potential people on their croos. 
    """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        
        qual_pk = self.kwargs['qualification_pk']
        qualification = QualificationTag.objects.get(pk=qual_pk)
    
        # let user know which croo they are in
        msg = 'You are currently scoring potential %s applications' 
        messages.info(self.request, msg % qualification)
        
        # we're just serving apps for the specified qualification
        # and don't care about limits to the total number of grades
        # TODO: stick this on the manager?
        # TODO: pass in the trips year? - tie grading to a trips_year url?
        application = (CrooSupplement.objects
                       .completed_applications(trips_year=TripsYear.objects.current())
                       .filter(grades__qualifications=qual_pk)
                       .filter(application__status=GeneralApplication.PENDING)
                       .exclude(grades__grader=self.request.user)
                       .order_by('?').first())
        if not application: 
            return reverse('applications:grade:no_croo_left')
        # pass along the croo's pk so that we can keep grading for this qualification
        return reverse('applications:grade:croo', kwargs={'pk': application.pk,
                                                          'qualification_pk': qual_pk})


class GradeCrooApplication(CrooGraderPermissionRequired, GenericGradingView):
    """ Grade a croo application """

    model = CrooApplicationGrade
    application_model = CrooSupplement
    skipped_grade_model = SkippedCrooGrade
    form_class = CrooApplicationGradeForm
    success_url = reverse_lazy('applications:grade:next_croo')
    verbose_application_name = 'Croo Application'

    def get_context_data(self, **kwargs):
        
        application = self.get_application()
        graders = list(map(lambda g: g.grader, application.grades.all()))
        kwargs['already_graded_by'] = graders
        # display extra fields regarding qualifications 

        yes_no = lambda field: 'yes' if field else 'no'
        kwargs['extra_fields'] = [
            ('Willing to be a Safety Lead?', yes_no(application.safety_lead_willing)),
            ('Medical Certifications', application.application.medical_certifications),
            ('Experience with medical certifications', application.application.medical_experience),
            ('Kitchen Witch/Kitchen Wizard willing?', yes_no(application.kitchen_lead_willing)),
            ('Kitchen Witch/Kitchen Wizard qualifications', application.kitchen_lead_qualifications)
        ]
        return super(GradeCrooApplication, self).get_context_data(**kwargs)


class GradeCrooApplicationForQualification(GradeCrooApplication):
    """
    Grade a croo application.

    Used if we are grading applications for a specific Croo. 
    This view passes along the target croo to the redirect dispatch
    view. 
    """

    def get_success_url(self):

        qual_pk = self.kwargs.get('qualification_pk')
        return reverse('applications:grade:next_croo', 
                       kwargs=dict(qual_pk=qual_pk))

    
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
    skipped_grade_model = SkippedLeaderGrade
    form_class = LeaderApplicationGradeForm
    success_url = reverse_lazy('applications:grade:next_leader')
    verbose_application_name = 'Trip Leader Application'


class NoLeaderApplicationsLeftToGrade(LeaderGraderPermissionRequired, 
                                      IfGradingAvailable, TemplateView):
    """ Tell user there are no more applications for her to grade """

    template_name = 'applications/no_applications.html'

        
