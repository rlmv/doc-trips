from django.conf.urls import include, url

from fyt.applications.views.application import (
    ApplicationAdminUpdate,
    ApplicationDetail,
    ApplicationIndex,
    ApplicationStatusUpdate,
    ApplicationUpdate,
    ContinueApplication,
    EditQuestions,
    NewApplication,
    SetupApplication,
)
from fyt.applications.views.assign import AssignToCroo, AssignToTrip
from fyt.applications.views.graders import GraderList
from fyt.applications.views.portal import (
    EditVolunteerPortalContent,
    VolunteerPortalView,
)
from fyt.applications.views.scoring import (
    DeleteScore,
    NoApplicationsLeftToScore,
    RedirectToNextScorableApplication,
    ScoreApplication,
    Scoring,
)
from fyt.db.urlhelpers import DB_REGEX


score_urlpatterns = [
    url(r'^$', Scoring.as_view(), name='scoring'),
    url(r'^none/$', NoApplicationsLeftToScore.as_view(),
        name='no_applications_left'),
    url(r'^next/$', RedirectToNextScorableApplication.as_view(),
        name='next'),
    url(r'^(?P<pk>[0-9]+)/$', ScoreApplication.as_view(),
        name='add'),
]

urlpatterns = [
    url(r'^$', VolunteerPortalView.as_view(), name='portal'),
    url(r'^setup/portal$', EditVolunteerPortalContent.as_view(),
        name='setup_portal'),
    url(r'^apply/$', NewApplication.as_view(), name='apply'),
    url(r'^apply/continue/$', ContinueApplication.as_view(), name='continue'),
    url(r'^setup/application$', SetupApplication.as_view(), name='setup'),
    url(r'^setup/questions$', EditQuestions.as_view(), name='setup_questions'),
    url(r'^score/', include(score_urlpatterns, namespace='score')),
]

# ----- protected database views ----------

application_urlpatterns = [
    url(DB_REGEX['LIST'], ApplicationIndex.as_view(), name='index'),
    url(DB_REGEX['DETAIL'], ApplicationDetail.as_view(), name='detail'),
    url(DB_REGEX['UPDATE'], ApplicationUpdate.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/update/status/$', ApplicationStatusUpdate.as_view(),
        name='update_status'),
    url(r'^(?P<pk>[0-9]+)/update/admin/$', ApplicationAdminUpdate.as_view(),
        name='update_admin'),
    url(r'^(?P<pk>[0-9]+)/update/trip/$', AssignToTrip.as_view(),
        name='update_trip'),
    url(r'^(?P<pk>[0-9]+)/update/croo/$', AssignToCroo.as_view(),
        name='update_croo'),
]

score_urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/delete/$', DeleteScore.as_view(), name='delete')
]

grader_urlpatterns = [
    url(r'^graders/$', GraderList.as_view(), name='graders_index'),
]
