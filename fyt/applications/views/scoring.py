import logging

from braces.views import FormMessagesMixin, SetHeadlineMixin
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.urls import reverse, reverse_lazy
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.functional import cached_property
from vanilla import CreateView, RedirectView, TemplateView

from fyt.applications.models import Score, Volunteer
from fyt.db.models import TripsYear
from fyt.db.views import DatabaseDeleteView
from fyt.permissions.views import GraderPermissionRequired
from fyt.timetable.models import Timetable
from fyt.utils.views import ExtraContextMixin


SHOW_SCORE_AVG_INTERVAL = 10
SKIP = 'skip'

logger = logging.getLogger(__name__)


class Scoring(GraderPermissionRequired, ExtraContextMixin, TemplateView):
    """
    Landing page for scoring.
    """
    template_name = 'applications/scoring.html'

    def extra_context(self):
        return {
            'progress': Volunteer.objects.score_progress(
                TripsYear.objects.current()
            )
        }


class IfScoringAvailable():
    """
    Only allow grading once applications are closed
    """
    def dispatch(self, request, *args, **kwargs):
        if not Timetable.objects.timetable().scoring_available:
            return render(request, 'applications/scoring_not_available.html')
        return super().dispatch(request, *args, **kwargs)


class NoApplicationsLeftToScore(GraderPermissionRequired,
                                IfScoringAvailable, TemplateView):
    """
    Tell user there are no more applications for her to grade
    """
    template_name = 'applications/no_applications.html'


class RedirectToNextScorableApplication(GraderPermissionRequired,
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


class ScoreForm(forms.ModelForm):

    class Meta:
        model = Score
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('question1', rows=1),
            Field('question2', rows=1),
            Field('question3', rows=1),
            Field('question4', rows=1),
            Field('question5', rows=1),
            Field('question6', rows=1),
            'score',
            Field('general', rows=3),
            FormActions(
                Submit('submit', 'Submit Score'),
                Submit(
                    'skip', 'Skip this Application',
                    css_class='btn-warning',
                    formnovalidate=True  # Disable browser validation
                ),
            )
        )


class ScoreApplication(GraderPermissionRequired, IfScoringAvailable,
                       ExtraContextMixin, SetHeadlineMixin, FormMessagesMixin,
                       CreateView):
    """
    Score a Volunteer application.
    """
    model = Score
    form_class = ScoreForm
    template_name = 'applications/grade.html'
    success_url = reverse_lazy('applications:score:next')
    form_invalid_message = 'Uh oh, looks like you forgot to fill out a field'

    def get_form_valid_message(self):
        return 'Score submitted for Application #{}'.format(self.kwargs['pk'])

    def get_headline(self):
        return 'Score {}: NetId {}'.format(
            self.application_name, self.application.applicant.netid)

    @cached_property
    def application(self):
        return get_object_or_404(Volunteer, pk=self.kwargs['pk'])

    @property
    def application_name(self):
        return "Application #{}".format(self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        self.show_average_grade(request.user)
        return super().get(request, *args, **kwargs)

    def show_average_grade(self, grader):
        """
        Show the grader their average grade every SHOW_GRADE_AVG_INTERVAL in
        a message.
        """
        scores = grader.scores.filter(trips_year=TripsYear.objects.current())

        if (scores.count() % SHOW_SCORE_AVG_INTERVAL == 0 and
                scores.count() != 0):
            avg_score = scores.aggregate(models.Avg('score'))['score__avg']

            msg = ("FYI, your average awarded score is {}. "
                   "You'll see your average score every {} grades.")
            self.messages.info(msg.format(avg_score, SHOW_SCORE_AVG_INTERVAL))

    def post(self, request, *args, **kwargs):
        """
        Check if the grader is skipping this application.
        """
        if SKIP in request.POST:
            self.application.skip(self.request.user)
            self.messages.success('Skipped {}'.format(self.application_name))
            return HttpResponseRedirect(self.get_success_url())

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.grader = self.request.user
        form.instance.application = self.application
        form.instance.trips_year = TripsYear.objects.current()
        return super().form_valid(form)

    def extra_context(self):
        return {
            'application': self.application,
            'score_choices': [desc for _, desc in Score.SCORE_CHOICES],
        }


class DeleteScore(DatabaseDeleteView):
    model = Score

    def get_success_url(self):
        return self.object.application.detail_url()
