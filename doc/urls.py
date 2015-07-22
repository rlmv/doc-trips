
from django.conf.urls import include, url
from django.contrib import admin
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from doc.views import HomePage
from doc.permissions import initialize_groups_and_permissions
from doc.core import urls as core_urls
from doc.users.models import DartmouthUser

admin.autodiscover()

# update the auth groups after each migration
@receiver(post_migrate)
def sync_auth(**kwargs):
    initialize_groups_and_permissions()

@receiver(post_migrate)
def make_sentinel_user(**kwargs):
    DartmouthUser.objects.sentinel()

handler403 = 'doc.views.permission_denied'

urlpatterns = [
    url(r'^$', HomePage.as_view(), name='home'),
    url(r'^users/', include('doc.users.urls', namespace='users')),
    url(r'^dartdm/', include('doc.dartdm.urls', namespace='dartdm')),      
    url(r'^permissions/', include('doc.permissions.urls', namespace='permissions')),
    url(r'^timetable/', include('doc.timetable.urls', namespace='timetable')),
    url(r'^db/', include('doc.db.urls', namespace='db')),
    url(r'^volunteers/', include('doc.applications.urls', namespace='applications')),
    url(r'^croos/', include('doc.croos.urls', namespace='croos')),
    url(r'^incoming/', include('doc.incoming.urls', namespace='incoming')),
    url(r'^core/', include(core_urls, namespace='core')),
    url(r'^admin/', include(admin.site.urls)),
]

