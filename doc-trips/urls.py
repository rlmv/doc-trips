from django.conf.urls import patterns, include, url

# default Django admin interface
from django.contrib import admin
admin.autodiscover()

from permissions import initialize_groups_and_permissions
initialize_groups_and_permissions()

from views import HomePage

urlpatterns = patterns('',
    url(r'^$', HomePage.as_view(), name='home'),
    url(r'^users/', include('users.urls', namespace='users')),
    url(r'^dartdm/', include('dartdm.urls', namespace='dartdm')),                   
    url(r'^permissions/', include('permissions.urls', namespace='permissions')),
    url(r'^timetable/', include('timetable.urls', namespace='timetable')),
    url(r'^db/', include('db.urls', namespace='db')),
    url(r'^leaders/', include('leaders.urls', namespace='leaders')),
    url(r'^croos/', include('croos.urls', namespace='croos')),                   
    url(r'^admin/', include(admin.site.urls)),
)

