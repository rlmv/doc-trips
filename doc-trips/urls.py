from django.conf.urls import patterns, include, url

# default Django admin interface
from django.contrib import admin
admin.autodiscover()

from permissions import initialize_groups_and_permissions
initialize_groups_and_permissions()

urlpatterns = patterns('',
    url(r'^$', 'views.index', name='home'),                      
    url(r'^user/', include('user.urls', namespace='user')),
    url(r'^dartdm/', include('dartdm.urls', namespace='dartdm')),                   
    url(r'^permissions/', include('permissions.urls', namespace='permissions')),
    url(r'^timetable/', include('timetable.urls', namespace='timetable')),
    url(r'^db/', include('db.urls', namespace='db')),
    url(r'^leader/', include('leader.urls', namespace='leader')),
    url(r'^admin/', include(admin.site.urls)),
)

