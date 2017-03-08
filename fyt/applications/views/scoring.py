import logging

from braces.views import FormMessagesMixin, SetHeadlineMixin
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from vanilla import CreateView, RedirectView, TemplateView

from fyt.applications.forms import (
    CrooApplicationGradeForm,
    LeaderApplicationGradeForm,
)
from fyt.applications.models import (
    Score,
    Volunteer
)
from fyt.db.models import TripsYear
from fyt.db.views import DatabaseDeleteView
from fyt.permissions.views import (
    CrooGraderPermissionRequired,
    LeaderGraderPermissionRequired,
)
from fyt.timetable.models import Timetable
from fyt.utils.views import ExtraContextMixin


SHOW_GRADE_AVG_INTERVAL = 10
SKIP = 'skip'

logger = logging.getLogger(__name__)


class Scoring(LeaderGraderPermissionRequired, TemplateView):
    """
    Landing page for scoring.
    """
    template_name = 'applications/scoring.html'


class IfScoringAvailable():
    """
    Only allow grading once applications are closed
    """
    def dispatch(self, request, *args, **kwargs):
        if not Timetable.objects.timetable().grading_available():
            return render(request, 'applications/scoring_not_available.html')
        return super().dispatch(request, *args, **kwargs)


class NoApplicationsLeftToScore(LeaderGraderPermissionRequired,
                                IfScoringAvailable, TemplateView):
    """
    Tell user there are no more applications for her to grade
    """
    template_name = 'applications/no_applications.html'


class RedirectToNextScorableApplication(LeaderGraderPermissionRequired,
                                        IfScoringAvailable, RedirectView):
    """
    Redirect to the next Volunteer application that needs to be scored.
    """
    permanent = False

    def get_redirect_url(self, *args, **kwargs):

        application = Volunteer.objects.next_to_score(self.request.user)

        if not application:
            return reverse('applications:score:no_applications_left')

        kwargs = {'pk': application.pk}
        return reverse('applications:score:add', kwargs=kwargs)


class ScoreApplication(LeaderGraderPermissionRequired, IfScoringAvailable,
                       ExtraContextMixin, SetHeadlineMixin, CreateView):
    """
    Score a Volunteer application.
    """
    model = Score
    fields = '__all__'
    template_name = 'applications/grade.html'
    success_url = reverse_lazy('applications:score:next')

    def get_headline(self):
        return 'Score Application #{}: NetId {}'.format(
            self.kwargs['pk'], self.application.applicant.netid
        )

    @cached_property
    def application(self):
        return get_object_or_404(Volunteer, pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        """
        Check if the grader is skipping this application.
        """
        if SKIP in request.POST:
            self.application.skip(self.request.user)
            return HttpResponseRedirect(self.get_success_url())

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.grader = self.request.user
        form.instance.application = self.application
        form.instance.trips_year = TripsYear.objects.current()
        return super().form_valid(form)

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

    def extra_context(self):
        return {
            'application': self.application,
            'score_choices': [desc for _, desc in Score.SCORE_CHOICES],
        }
