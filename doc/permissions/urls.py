
from django.conf.urls import patterns, url

from doc.permissions.views import SetPermissions

urlpatterns = patterns('', 
    url(r'^set/$', SetPermissions.as_view(), name='set_permissions'),
)
