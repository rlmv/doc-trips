
from django.conf.urls import patterns, url, include

from db.urlhelpers import DB_REGEX
from applications.views.application import (NewApplication, ContinueApplication, 
                                            SetupApplication,
                                            ApplicationDatabaseListView, 
                                            LeaderApplicationDatabaseListView, 
                                            LeaderApplicationDatabaseDetailView, 
                                            LeaderApplicationDatabaseUpdateView,)

from applications.views.grading import(RedirectToNextGradableCrooApplication,
                                       GradeCrooApplication,
                                       NoCrooApplicationsLeftToGrade)

  
grade_urlpatterns = patterns(
    '',
    url(r'^croos/$', RedirectToNextGradableCrooApplication.as_view(), name='next_croo'),
    url(r'^croos/(?P<pk>[0-9]+)$', GradeCrooApplication.as_view(), name='croo'),
    url(r'^croos/none/$', NoCrooApplicationsLeftToGrade.as_view(), name='no_croo_left'),
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
    url(DB_REGEX['UPDATE'], LeaderApplicationDatabaseUpdateView.as_view(), name='leadersupplement_update'),
)

application_urlpatterns = patterns(
    '',
    url(DB_REGEX['LIST'], ApplicationDatabaseListView.as_view(), name='application_index'),
    url(r'^leaders/', include(_leaderapplication_urlpatterns)),
)

