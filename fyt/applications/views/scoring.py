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
    Volunteer
)
from fyt.db.models import TripsYear
from fyt.db.views import DatabaseDeleteView
from fyt.permissions.views import (
    CrooGraderPermissionRequired,
    LeaderGraderPermissionRequired,
)
from fyt.timetable.models import Timetable


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
