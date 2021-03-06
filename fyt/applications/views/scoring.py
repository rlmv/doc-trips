import logging

from braces.views import FormMessagesMixin, SetHeadlineMixin
from django import forms
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from vanilla import CreateView, FormView, RedirectView, TemplateView

from fyt.applications.forms import SKIP, ScoreForm, ScoreQuestionFormset
from fyt.applications.models import Grader, Score, ScoreClaim, ScoreQuestion, Volunteer
from fyt.core.models import TripsYear
from fyt.core.views import DatabaseDeleteView
from fyt.permissions.views import GraderPermissionRequired, SettingsPermissionRequired
from fyt.timetable.models import Timetable
from fyt.utils.views import ExtraContextMixin


SHOW_SCORE_AVG_INTERVAL = 10
HOLD_DURATION = ScoreClaim.HOLD_DURATION

logger = logging.getLogger(__name__)


class Scoring(GraderPermissionRequired, ExtraContextMixin, TemplateView):
    """
    Landing page for scoring.
    """

    template_name = 'applications/scoring.html'

    @cached_property
    def trips_year(self):
        return TripsYear.objects.current()

    def extra_context(self):
        return {
            'trips_year': self.trips_year,
            'progress': Volunteer.objects.score_progress(self.trips_year),
        }


class IfScoringAvailable:
    """
    Only allow grading once applications are closed
    """

    def dispatch(self, request, *args, **kwargs):
        if not Timetable.objects.timetable().scoring_available:
            return render(request, 'applications/scoring_not_available.html')
        return super().dispatch(request, *args, **kwargs)


class NoApplicationsLeftToScore(
    GraderPermissionRequired, IfScoringAvailable, TemplateView
):
    """
    Tell user there are no more applications for her to grade
    """

    template_name = 'applications/no_applications.html'


class ClaimNextApplication(GraderPermissionRequired, IfScoringAvailable, RedirectView):
    """
    Redirect to the next Volunteer application that needs to be scored.
    """

    permanent = False

    @property
    def grader(self):
        return Grader.objects.from_user(self.request.user)

    def get_redirect_url(self, *args, **kwargs):
        application = self.grader.claim_next_to_score()

        if not application:
            return reverse('applications:score:no_applications_left')

        return reverse('applications:score:add', kwargs={'pk': application.pk})


class ScoreApplication(
    GraderPermissionRequired,
    IfScoringAvailable,
    ExtraContextMixin,
    SetHeadlineMixin,
    FormMessagesMixin,
    CreateView,
):
    """
    Score a Volunteer application.
    """

    model = Score
    form_class = ScoreForm
    template_name = 'applications/grade.html'
    success_url = reverse_lazy('applications:score:next')
    form_invalid_message = 'Uh oh, looks like you forgot to fill out a field'

    @property
    def application_name(self):
        return "Application #{}".format(self.kwargs['pk'])

    def get_form_valid_message(self):
        return 'Score submitted for {}'.format(self.application_name)

    def get_headline(self):
        return 'Score {}: NetId {}'.format(
            self.application_name, self.application.applicant.netid
        )

    @cached_property
    def trips_year(self):
        return TripsYear.objects.current()

    @cached_property
    def application(self):
        return get_object_or_404(Volunteer, pk=self.kwargs['pk'])

    @cached_property
    def grader(self):
        return Grader.objects.from_user(self.request.user)

    @cached_property
    def claim(self):
        return self.grader.active_claim(self.application)

    def get(self, *args, **kwargs):
        if not self.claim:
            self.messages.warning(
                "You took longer than the alloted time " "for scoring this application"
            )
            return HttpResponseRedirect(self.get_success_url())

        self.show_average_grade()
        return super().get(*args, **kwargs)

    def show_average_grade(self):
        """
        Show the grader their average grade every SHOW_GRADE_AVG_INTERVAL in
        a message.
        """
        score_count = self.grader.score_count(self.trips_year)

        if score_count % SHOW_SCORE_AVG_INTERVAL == 0 and score_count != 0:
            msg = (
                "FYI, your average awarded leader score is {}. "
                "Your average awarded croo score is {}. "
                "You'll see your average score every {} grades."
            )
            self.messages.info(
                msg.format(
                    self.grader.avg_leader_score(self.trips_year),
                    self.grader.avg_croo_score(self.trips_year),
                    SHOW_SCORE_AVG_INTERVAL,
                )
            )

    def post(self, request, *args, **kwargs):
        """
        Check if the grader is skipping this application.
        """
        if SKIP in request.POST:
            self.grader.skip(self.application)
            self.messages.success('Skipped {}'.format(self.application_name))
            return HttpResponseRedirect(self.get_success_url())

        if not self.claim:
            self.messages.warning(
                "You took longer than the alloted time " "for scoring this application"
            )
            return HttpResponseRedirect(self.get_success_url())

        return super().post(request, *args, **kwargs)

    def get_form(self, **kwargs):
        return ScoreForm(self.application, self.grader, **kwargs)

    def extra_context(self):
        return {
            'application': self.application,
            'time_left': self.claim.time_left(),
            'timeout_url': reverse('applications:score:scoring'),
        }


class DeleteScore(DatabaseDeleteView):
    model = Score

    def get_success_url(self):
        return self.object.application.detail_url()


class EditScoreQuestions(SettingsPermissionRequired, FormMessagesMixin, FormView):
    template_name = 'applications/score_questions.html'
    success_url = reverse_lazy('applications:setup_scoring')
    form_valid_message = "Score questions successfully updated"
    form_invalid_message = "There is an issue with the form"

    @cached_property
    def trips_year(self):
        return TripsYear.objects.current()

    def get_queryset(self):
        return ScoreQuestion.objects.filter(trips_year=self.trips_year)

    def get_form(self, **kwargs):
        return ScoreQuestionFormset(
            trips_year=self.trips_year, queryset=self.get_queryset(), **kwargs
        )

    def form_valid(self, formset):
        formset.save()
        return super().form_valid(formset)
