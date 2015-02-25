from django.conf.urls import patterns, include, url

# default Django admin interface
from django.contrib import admin
admin.autodiscover()

from doc.permissions import initialize_groups_and_permissions
initialize_groups_and_permissions()

from doc.views import HomePage

urlpatterns = patterns('',
    url(r'^$', HomePage.as_view(), name='home'),
    url(r'^users/', include('doc.users.urls', namespace='users')),
    url(r'^dartdm/', include('doc.dartdm.urls', namespace='dartdm')),                   
    url(r'^permissions/', include('doc.permissions.urls', namespace='permissions')),
    url(r'^timetable/', include('doc.timetable.urls', namespace='timetable')),
    url(r'^db/', include('doc.db.urls', namespace='db')),
    url(r'^applications/', include('doc.applications.urls', namespace='applications')),
#    url(r'^leaders/', include('doc.leaders.urls', namespace='leaders')),
    url(r'^croos/', include('doc.croos.urls', namespace='croos')),                   
    url(r'^admin/', include(admin.site.urls)),
)

