
from django.conf.urls import patterns, url

from permissions.views import SetPermissions, dnd_lookup

urlpatterns = patterns('', 
    url(r'^set/$', SetPermissions.as_view(), name='set_permissions'),
    url(r'^dnd/lookup/$', dnd_lookup, name='dnd_lookup'),     
)
