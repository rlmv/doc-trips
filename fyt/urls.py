
from django.conf.urls import include, url
from django.contrib import admin
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from fyt.views import HomePage, RaiseError
from fyt.permissions import initialize_groups_and_permissions
from fyt.users.models import DartmouthUser
from fyt.incoming.urls import settings_urlpatterns

admin.autodiscover()


# update the auth groups after each migration
@receiver(post_migrate)
def sync_auth(**kwargs):
    initialize_groups_and_permissions()


@receiver(post_migrate)
def make_sentinel_user(**kwargs):
    DartmouthUser.objects.sentinel()

handler403 = 'fyt.views.permission_denied'


urlpatterns = [
    url(r'^$', HomePage.as_view(), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^dartdm/', include('fyt.dartdm.urls', namespace='dartdm')),
    url(r'^db/', include('fyt.db.urls', namespace='db')),
    url(r'^incoming/', include('fyt.incoming.urls', namespace='incoming')),
    url(r'^permissions/', include('fyt.permissions.urls', namespace='permissions')),
    # TODO: move this to a better namespace / general settings namespace
    url(r'^settings/', include(settings_urlpatterns, namespace='settings')),
    url(r'^test/error/', RaiseError.as_view(), name='raise_error'),
    url(r'^timetable/', include('fyt.timetable.urls', namespace='timetable')),
    url(r'^users/', include('fyt.users.urls', namespace='users')),
    url(r'^volunteers/', include('fyt.applications.urls', namespace='applications')),
]
