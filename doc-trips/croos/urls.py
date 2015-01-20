

from django.conf.urls import patterns, url, include
from croos.views import CrooApplicationView

urlpatterns = patterns('', 
    url(r'^apply/$', CrooApplicationView.as_view(), name='apply'),
)
