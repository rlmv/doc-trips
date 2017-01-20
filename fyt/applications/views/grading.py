import logging

from braces.views import FormMessagesMixin
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from vanilla import FormView, RedirectView, TemplateView

from fyt.applications.forms import (
    CrooApplicationGradeForm,
    LeaderApplicationGradeForm,
)
from fyt.applications.models import (
    CrooApplicationGrade,
    CrooSupplement,
    LeaderApplicationGrade,
    LeaderSupplement,
    QualificationTag,
    SkippedCrooGrade,
    SkippedLeaderGrade,
)
from fyt.db.models import TripsYear
from fyt.db.views import DatabaseDeleteView
from fyt.permissions.views import (
    CrooGraderPermissionRequired,
    LeaderGraderPermissionRequired,
)
from fyt.timetable.models import Timetable


"""
These views contain all the logic for grading Croo and Leader applications.

Both sets of applications follow the same general pattern:
(1) Redirect page: finds the next application for this grader,
and redirects to
(2) the Grading page, which accepts a grade form submission and
returns the grader to the Redirect view.

However, there are some subtleties which complicate matters:

(1) Croo graders tag Croo applications with Qualifications for
certian croos. There is a special provision which lets Croo heads
grade ONLY applications which have a certain qualification. This
allows Croo heads to do a once-over of their potential croo members.

(2) In order to accomodate this there is a subclass of Croo Redirect and
Grading Views which pass around the pk of the targeted Qualification.

(3) Skipping. Graders can skip applications which they recognize. When
they do so, an appropriate SkippedGrade object is created which links
the grader to the skipped application. Once a grader has skipped an
application they will not see it again, UNLESS:

(4) the grader is a Croo Head. If a Croo Head skips a Croo application in
the normal grading process, and this application has been tagged as
qualified for this Head's Croo, the Croo head will see the application
again in the Qualification-specific grading view. However, if the Croo head
then skips the application (eg. because the Head sees that a co-head has
already graded it) then the application will not be shown to the Head again.

Whew.
"""

SHOW_GRADE_AVG_INTERVAL = 10
SKIP = 'skip'

logger = logging.getLogger(__name__)


class GraderLandingPage(TemplateView):

    template_name = 'applications/graders.html'

    def get_context_data(self, **kwargs):
        kwargs['qualifications'] = QualificationTag.objects.filter(
            trips_year=TripsYear.objects.current()
        )
        return super().get_context_data(**kwargs)


class IfGradingAvailable():
    """
    Only allow grading once applications are closed
    """
    def dispatch(self, request, *args, **kwargs):
        if not Timetable.objects.timetable().grading_available():
            return render(request, 'applications/grading_not_available.html')
        return super().dispatch(request, *args, **kwargs)


class GenericGradingView(IfGradingAvailable, FormMessagesMixin, FormView):
    """
    Shared logic for grading Croo and Leader applications.
    """
    grade_model = None
    application_model = None
    skipped_grade_model = None
    form_class = None
    success_url = None
    verbose_application_name = None  # eg. "Trip Leader Application"
    template_name = 'applications/grade.html'
    form_invalid_message = 'Uh oh, looks like you forgot to fill out a field'

    def get_form_valid_message(self):
        return 'Score submitted for %s #%s' % (
            self.verbose_application_name, self.kwargs['pk']
        )

    def get(self, request, *args, **kwargs):
        """
        Message the grader their average grade
        """
        self.check_and_show_average_grade(request.user)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Check whether the grader is skipping this application
        """
        if SKIP in request.POST:
            logger.info(
                '%s skipped %s %s' % (
                    self.request.user,
                    self.verbose_application_name,
                    self.kwargs['pk']
                ))
            self.skip_application()
            return HttpResponseRedirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def get_application(self):
        """
        Return the Croo or Leader application to grade
        """
        return get_object_or_404(self.application_model, pk=self.kwargs['pk'])

    def skip_application(self):
        """
        Skip this application.

        Creates a skipped grade object so that this grader won't see
        this application again.
        """

        application = self.get_application()
        self.skipped_grade_model.objects.create(
            trips_year=application.trips_year,
            application=application,
            grader=self.request.user,
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        application = self.get_application()
        context['application'] = application
        context['title'] = 'Score %s #%s: NetId %s' % (
            self.verbose_application_name, self.kwargs['pk'],
            application.application.applicant.netid
        )
        context['score_choices'] = map(
            lambda c: c[1], self.grade_model.SCORE_CHOICES
        )
        return context

    def check_and_show_average_grade(self, grader):
        """
        Show grader their average grade.

        Every SHOW_GRADE_AVG_INTERVAL tell the grader what their
        average grade has been (for this year, of course). Displayed
        in a message.
        """
        ct = ContentType.objects.get_for_model(self.grade_model)
        grades = (
            getattr(self.request.user, ct.model + 's')
            .filter(trips_year=TripsYear.objects.current())
        )
        if (grades.count() % SHOW_GRADE_AVG_INTERVAL == 0 and grades.count() != 0):
            avg_grade = grades.aggregate(models.Avg('grade'))['grade__avg']
            msg = (
                "Hey, just FYI your average awarded %s is %s. "
                "We'll show you your average score every %s grades."
            )
            self.messages.info(msg % (
                self.grade_model._meta.verbose_name,
                avg_grade, SHOW_GRADE_AVG_INTERVAL
            ))

    def form_valid(self, form):
        """
        Add the grader and application to the grade
        """
        form.instance.grader = self.request.user
        form.instance.application = self.get_application()
        form.instance.trips_year = TripsYear.objects.current()
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self, **kwargs):
        """
        Add a Skip button to the form
        """
        form = super().get_form(**kwargs)
        form.helper = FormHelper(form)
        form.helper.layout.append(
            FormActions(
                Submit('submit', 'Submit Score'),
                Submit('skip', 'Skip this Application',
                       css_class='btn-warning'),
            )
        )
        return form


class RedirectToNextGradableCrooApplication(
        CrooGraderPermissionRequired, IfGradingAvailable, RedirectView):
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


class RedirectToNextGradableCrooApplicationForQualification(
        CrooGraderPermissionRequired, IfGradingAvailable, RedirectView):
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

        # let user know which qualification they are scoring
        msg = 'You are currently scoring potential %s applications'
        messages.info(self.request, msg % qualification)

        application = CrooSupplement.objects.next_to_grade_for_qualification(
            self.request.user, qualification
        )

        if not application:
            return reverse('applications:grade:no_croo_left')

        # pass along the qualifications's pk so that we can keep
        # grading for this qualification
        kwargs = {'pk': application.pk, 'qualification_pk': qual_pk}
        return reverse('applications:grade:croo', kwargs=kwargs)


class GradeCrooApplication(CrooGraderPermissionRequired, GenericGradingView):
    """
    Grade a croo application
    """
    grade_model = CrooApplicationGrade
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
            ('Willing to be a Safety Lead?',
             yes_no(application.safety_lead_willing)),
            ('Medical Certifications',
             application.application.medical_certifications),
            ('Experience with medical certifications',
             application.application.medical_experience),
            ('Kitchen Witch/Kitchen Wizard willing?',
             yes_no(application.kitchen_lead_willing)),
            ('Kitchen Witch/Kitchen Wizard qualifications',
             application.kitchen_lead_qualifications)
        ]
        return super().get_context_data(**kwargs)


class GradeCrooApplicationForQualification(GradeCrooApplication):
    """
    Grade a croo application.

    Used if we are grading applications for a specific Croo.
    This view passes along the target croo to the redirect dispatch
    view.
    """
    def skip_application(self):
        """
        Skip this application.

        Creates a skipped grade object so that this grader won't see
        this application again. Since we are grading for a particular
        qualification, add the qualification to the Skip.
        """
        application = self.get_application()
        self.skipped_grade_model.objects.create(
            trips_year=application.trips_year,
            application=application,
            grader=self.request.user,
            for_qualification_id=self.kwargs['qualification_pk']
        )

    def get_success_url(self):
        qual_pk = self.kwargs.get('qualification_pk')
        return reverse('applications:grade:next_croo',
                       kwargs=dict(qualification_pk=qual_pk))


class NoCrooApplicationsLeftToGrade(CrooGraderPermissionRequired,
                                    IfGradingAvailable, TemplateView):
    template_name = 'applications/no_applications.html'


class RedirectToNextGradableLeaderApplication(LeaderGraderPermissionRequired,
                                              IfGradingAvailable, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        """
        Return the url of the next LeaderApplication that needs grading
        """
        application = LeaderSupplement.objects.next_to_grade(
            self.request.user
        )
        if not application:
            return reverse('applications:grade:no_leaders_left')

        kwargs = {'pk': application.pk}
        return reverse('applications:grade:leader', kwargs=kwargs)


class GradeLeaderApplication(LeaderGraderPermissionRequired,
                             GenericGradingView):
    grade_model = LeaderApplicationGrade
    application_model = LeaderSupplement
    skipped_grade_model = SkippedLeaderGrade
    form_class = LeaderApplicationGradeForm
    success_url = reverse_lazy('applications:grade:next_leader')
    verbose_application_name = 'Trip Leader Application'


class NoLeaderApplicationsLeftToGrade(LeaderGraderPermissionRequired,
                                      IfGradingAvailable, TemplateView):
    """
    Tell user there are no more applications for her to grade
    """
    template_name = 'applications/no_applications.html'


class DeleteLeaderGrade(DatabaseDeleteView):
    model = LeaderApplicationGrade

    def get_success_url(self):
        return self.object.application.application.detail_url()


class DeleteCrooGrade(DatabaseDeleteView):
    model = CrooApplicationGrade

    def get_success_url(self):
        return self.object.application.application.detail_url()
