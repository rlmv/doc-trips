
from django.conf.urls import patterns, url

from leader.views import *

urlpatterns = patterns('', 
    url(r'^(?P<pk>[0-9]+)$', edit_leaderapplication, name='leaderapplication'),
    url(r'^apply/$', create_leaderapplication, name='create_leaderapplication'),    
    url(r'^grade/$', redirect_to_next_gradable_application, name='grade_random'),
    url(r'^grade/(?P<pk>[0-9]+)$', grade_application, name='grade'),
)

leaderapplication_urlpatterns = LeaderApplicationDatabaseViews.get_urls()
                              
