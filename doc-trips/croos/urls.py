

from django.conf.urls import patterns, url, include
from croos.views import CrooApplicationView, CrooApplicationCreate, CreateCrooApplication

urlpatterns = patterns('', 
    url(r'^apply/$', CrooApplicationCreate.as_view(), name='apply'),
    url(r'^apply/edit$', CrooApplicationView.as_view(), name='edit_application'),
    url(r'^createapplication/$', CreateCrooApplication.as_view(), name='create_application'),                   
)
