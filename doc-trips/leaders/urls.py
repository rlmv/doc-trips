
from django.conf.urls import patterns, url

from db.urlhelpers import DB_REGEX
from leaders.views import *

urlpatterns = patterns('',
    url(r'^apply/$', LeaderApply.as_view(), name='apply'),
    url(r'^createapplication/$', CreateLeaderApplication.as_view(), name='create_application'),                   
    url(r'^grade/$', RedirectToNextGradableApplication.as_view(), name='grade_random'),
    url(r'^grade/(?P<pk>[0-9]+)$', GradeApplication.as_view(), name='grade'),
    url(r'^grade/none$', NoApplicationToGrade.as_view(), name='no_application'),
)

leaderapplication_urlpatterns = patterns('', 
    url(DB_REGEX['LIST'], LeaderApplicationDatabaseListView.as_view(), name='leaderapplication_index'),
    LeaderApplicationDatabaseUpdateView.urlpattern(),
    LeaderApplicationDatabaseDetailView.urlpattern(),
    url(r'^(?P<pk>[0-9]+)/assign$', LeaderApplicationDatabaseAssignmentView.as_view(), name='leaderapplication_assignment'),
 )                                         
                              
