
from django.conf.urls import patterns, url

from leader.views import *

urlpatterns = patterns('',
    url(r'^apply/$', LeaderApply.as_view(), name='apply'),
    url(r'^apply/(?P<pk>[0-9]+)$', EditLeaderApplication.as_view(), name='edit_application'),
    url(r'^grade/$', RedirectToNextGradableApplication.as_view(), name='grade_random'),
    url(r'^grade/(?P<pk>[0-9]+)$', GradeApplication.as_view(), name='grade'),
    url(r'^grade/none$', NoApplicationToGrade.as_view(), name='no_application'),
)

leaderapplication_urlpatterns = patterns('', 
    LeaderApplicationDatabaseListView.urlpattern(),
    LeaderApplicationDatabaseUpdateView.urlpattern(),
)                                         
                              
