
from django.conf.urls import patterns, url

from permissions.views import SetPermissions

urlpatterns = patterns('', 
    url(r'^set/$', SetPermissions.as_view(), name='set_permissions'),
)
