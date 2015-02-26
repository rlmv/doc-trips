
from django.conf.urls import patterns, url, include

from doc.db.urlhelpers import DB_REGEX
from doc.applications.views.application import (NewApplication, ContinueApplication, 
                                            SetupApplication,
                                            ApplicationDatabaseListView, 
                                            ApplicationDatabaseDetailView,
                                            ApplicationDatabaseUpdateView,
                                            LeaderApplicationDatabaseListView, 
                                            LeaderApplicationDatabaseDetailView,)
 

from doc.applications.views.grading import(RedirectToNextGradableCrooApplication,
                                       GradeCrooApplication,
                                       NoCrooApplicationsLeftToGrade,
                                       RedirectToNextGradableLeaderApplication,
                                       GradeLeaderApplication,
                                       NoLeaderApplicationsLeftToGrade,)

  
grade_urlpatterns = patterns(
    '',
    url(r'^croos/$', RedirectToNextGradableCrooApplication.as_view(), name='next_croo'),
    url(r'^croos/(?P<pk>[0-9]+)$', GradeCrooApplication.as_view(), name='croo'),
    url(r'^croos/none/$', NoCrooApplicationsLeftToGrade.as_view(), name='no_croo_left'),    
    url(r'^leaders/$', RedirectToNextGradableLeaderApplication.as_view(), name='next_leader'),
    url(r'^leaders/(?P<pk>[0-9]+)$', GradeLeaderApplication.as_view(), name='leader'),
    url(r'^leaders/none/$', NoLeaderApplicationsLeftToGrade.as_view(), name='no_leaders_left'),
)

urlpatterns = patterns(
    '',
    url(r'^apply/$', NewApplication.as_view(), name='apply'),
    url(r'^continue/$', ContinueApplication.as_view(), name='continue'),
    url(r'^setup/$', SetupApplication.as_view(), name='setup'),
    url(r'^grade/', include(grade_urlpatterns, namespace='grade')),
)

# TODO: fix leaderapplication, leadersupplement mismatch

_leaderapplication_urlpatterns = patterns(
    '',
    url(DB_REGEX['LIST'], LeaderApplicationDatabaseListView.as_view(), name='leaderapplication_index'),
    url(DB_REGEX['DETAIL'], LeaderApplicationDatabaseDetailView.as_view(), name='leadersupplement_detail'),
)

application_urlpatterns = patterns(
    '',
    url(DB_REGEX['LIST'], ApplicationDatabaseListView.as_view(), name='application_index'),
    url(DB_REGEX['DETAIL'], ApplicationDatabaseDetailView.as_view(), name='generalapplication_detail'),
    url(DB_REGEX['UPDATE'], ApplicationDatabaseUpdateView.as_view(), name='generalapplication_update'),
    url(r'^leaders/', include(_leaderapplication_urlpatterns)),
)

