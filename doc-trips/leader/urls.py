
from django.conf.urls import patterns, url

from leader.views import *

urlpatterns = patterns('', 
    url(r'^apply/$', LeaderApply.as_view(), name='create_leaderapplication'),    
    url(r'^apply/(?P<pk>[0-9]+)$', EditLeaderApplication.as_view(), name='leaderapplication'),
    url(r'^grade/$', redirect_to_next_gradable_application, name='grade_random'),
    url(r'^grade/(?P<pk>[0-9]+)$', GradeApplication.as_view(), name='grade'),
)

leaderapplication_urlpatterns = patterns('', 
    LeaderApplicationListView.urlpattern(),
    LeaderApplicationUpdateView.urlpattern(),
)                                         
                              
