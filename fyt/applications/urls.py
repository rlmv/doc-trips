
from django.conf.urls import include, url

from fyt.applications.views.application import (
    ApplicationAdminUpdate,
    ApplicationCertsUpdate,
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
from fyt.applications.views.grading import (
    DeleteCrooGrade,
    DeleteLeaderGrade,
    GradeCrooApplication,
    GradeCrooApplicationForQualification,
    GradeLeaderApplication,
    GraderLandingPage,
    NoCrooApplicationsLeftToGrade,
    NoLeaderApplicationsLeftToGrade,
    RedirectToNextGradableCrooApplication,
    RedirectToNextGradableCrooApplicationForQualification,
    RedirectToNextGradableLeaderApplication,
)
from fyt.applications.views.portal import (
    EditVolunteerPortalContent,
    VolunteerPortalView,
)
from fyt.db.urlhelpers import DB_REGEX


grade_urlpatterns = [
    url(r'^$', GraderLandingPage.as_view(), name='graders'),
    url(r'^croos/$', RedirectToNextGradableCrooApplication.as_view(),
        name='next_croo'),
    url(r'^croos/(?P<pk>[0-9]+)/$', GradeCrooApplication.as_view(),
        name='croo'),
    url(r'^croos/for/(?P<qualification_pk>[0-9]+)/$',
        RedirectToNextGradableCrooApplicationForQualification.as_view(),
        name='next_croo'),
    url(r'^croos/for/(?P<qualification_pk>[0-9]+)/(?P<pk>[0-9]+)/$',
        GradeCrooApplicationForQualification.as_view(), name='croo'),
    url(r'^croos/none/$', NoCrooApplicationsLeftToGrade.as_view(),
        name='no_croo_left'),
    url(r'^leaders/$', RedirectToNextGradableLeaderApplication.as_view(),
        name='next_leader'),
    url(r'^leaders/(?P<pk>[0-9]+)$', GradeLeaderApplication.as_view(),
        name='leader'),
    url(r'^leaders/none/$', NoLeaderApplicationsLeftToGrade.as_view(),
        name='no_leaders_left'),
]

urlpatterns = [
    url(r'^$', VolunteerPortalView.as_view(), name='portal'),
    url(r'^setup/portal$', EditVolunteerPortalContent.as_view(),
        name='setup_portal'),
    url(r'^apply/$', NewApplication.as_view(), name='apply'),
    url(r'^apply/continue/$', ContinueApplication.as_view(), name='continue'),
    url(r'^setup/application$', SetupApplication.as_view(), name='setup'),
    url(r'^setup/questions$', EditQuestions.as_view(), name='setup_questions'),
    url(r'^grade/', include(grade_urlpatterns, namespace='grade')),
]

# ----- protected database views ----------

application_urlpatterns = [
    url(DB_REGEX['LIST'], ApplicationIndex.as_view(), name='index'),
    url(DB_REGEX['DETAIL'], ApplicationDetail.as_view(), name='detail'),
    url(DB_REGEX['UPDATE'], ApplicationUpdate.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/update/status/$', ApplicationStatusUpdate.as_view(),
        name='update_status'),
    url(r'^(?P<pk>[0-9]+)/update/trainings/$', ApplicationCertsUpdate.as_view(),
        name='update_trainings'),
    url(r'^(?P<pk>[0-9]+)/update/admin/$', ApplicationAdminUpdate.as_view(),
        name='update_admin'),
    url(r'^(?P<pk>[0-9]+)/update/trip/$', AssignToTrip.as_view(),
        name='update_trip'),
    url(r'^(?P<pk>[0-9]+)/update/croo/$', AssignToCroo.as_view(),
        name='update_croo'),
]

leadergrade_urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/delete/$', DeleteLeaderGrade.as_view(),
        name='delete'),
]

croograde_urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/delete/$', DeleteCrooGrade.as_view(), name='delete'),
]

grader_urlpatterns = [
    url(r'^graders/$', GraderList.as_view(), name='graders_index'),
]
