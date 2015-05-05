
from django.conf.urls import include, url
from django.contrib import admin

from doc.views import HomePage
from doc.permissions import initialize_groups_and_permissions

admin.autodiscover()
initialize_groups_and_permissions()
handler403 = 'doc.views.permission_denied'

urlpatterns = [
    url(r'^$', HomePage.as_view(), name='home'),
    url(r'^users/', include('doc.users.urls', namespace='users')),
    url(r'^dartdm/', include('doc.dartdm.urls', namespace='dartdm')),      
    url(r'^permissions/', include('doc.permissions.urls', namespace='permissions')),
    url(r'^timetable/', include('doc.timetable.urls', namespace='timetable')),
    url(r'^db/', include('doc.db.urls', namespace='db')),

    url(r'^volunteers/', include('doc.applications.urls', namespace='applications')),
    # TODO: remove the 'applications' urls in favor of 'volunteers'
    url(r'^applications/', include('doc.applications.urls', namespace='applications')),

    url(r'^croos/', include('doc.croos.urls', namespace='croos')),
    url(r'^incoming/', include('doc.incoming.urls', namespace='incoming')),
    url(r'^admin/', include(admin.site.urls)),
]

