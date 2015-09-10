
from django.conf.urls import url, include

from fyt.db.urlhelpers import DB_REGEX
from fyt.applications.views.application import (
    NewApplication,
    ContinueApplication,
    SetupApplication,
    ApplicationIndex,
    ApplicationDetail,
    ApplicationUpdate,
    ApplicationStatusUpdate,
    ApplicationCertsUpdate,
    ApplicationAdminUpdate)
from fyt.applications.views.grading import(
    RedirectToNextGradableCrooApplication,
    RedirectToNextGradableCrooApplicationForQualification,
    GradeCrooApplication,
    GradeCrooApplicationForQualification,
    NoCrooApplicationsLeftToGrade,
    RedirectToNextGradableLeaderApplication,
    GradeLeaderApplication,
    NoLeaderApplicationsLeftToGrade,
    GraderLandingPage,
    DeleteCrooGrade,
    DeleteLeaderGrade)
from fyt.applications.views.assign import AssignToTrip, AssignToCroo
from fyt.applications.views.graders import GraderList
from fyt.applications.views.portal import (
    VolunteerPortalView, EditVolunteerPortalContent
)


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
    url(r'^grade/', include(grade_urlpatterns, namespace='grade')),
]

# ----- protected database views ----------

application_urlpatterns = [
    url(DB_REGEX['LIST'], ApplicationIndex.as_view(),
        name='application_index'),
    url(DB_REGEX['DETAIL'], ApplicationDetail.as_view(),
        name='generalapplication_detail'),
    url(DB_REGEX['UPDATE'], ApplicationUpdate.as_view(),
        name='generalapplication_update'),
    url(r'^(?P<pk>[0-9]+)/update/status/$',
        ApplicationStatusUpdate.as_view(),
        name='update_application_status'),
    url(r'^(?P<pk>[0-9]+)/update/trainings/$',
        ApplicationCertsUpdate.as_view(),
        name='update_application_trainings'),
    url(r'^(?P<pk>[0-9]+)/update/trip$', AssignToTrip.as_view(),
        name='update_trip_assignment'),
    url(r'^(?P<pk>[0-9]+)/update/croo/$', AssignToCroo.as_view(),
        name='update_croo_assignment'),
    url(r'^(?P<pk>[0-9]+)/update/admin/$',
        ApplicationAdminUpdate.as_view(),
        name='update_application_admin'),
]

grade_urlpatterns = [
    url(r'^leader/(?P<pk>[0-9]+)/delete/$', DeleteLeaderGrade.as_view(),
        name='leaderapplicationgrade_delete'),
    url(r'^croo/(?P<pk>[0-9]+)/delete/$', DeleteCrooGrade.as_view(),
        name='crooapplicationgrade_delete'),
    url(r'^graders/$', GraderList.as_view(), name='graders_index'),
]
