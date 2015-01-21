

from django.conf.urls import patterns, url, include
from croos.views import CrooApplicationView, CrooApplicationCreate

urlpatterns = patterns('', 
    url(r'^apply/$', CrooApplicationCreate.as_view(), name='apply'),
    url(r'^apply/edit$', CrooApplicationView.as_view(), name='edit_application'),
)
