from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from fyt.incoming.urls import settings_urlpatterns
from fyt.permissions.permissions import groups
from fyt.views import HomePage, RaiseError


admin.autodiscover()

handler403 = 'fyt.views.permission_denied'

urlpatterns = [
    url(r'^$', HomePage.as_view(), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^dartdm/', include(('fyt.dartdm.urls', 'dartdm'))),
    url(r'^db/', include(('fyt.core.urls', 'core'))),
    url(r'^incoming/', include(('fyt.incoming.urls', 'incoming'))),
    url(r'^permissions/', include(('fyt.permissions.urls', 'permissions'))),
    # TODO: move this to a better namespace / general settings namespace
    url(r'^settings/', include((settings_urlpatterns, 'settings'))),
    url(r'^test/error/', RaiseError.as_view(), name='raise_error'),
    url(r'^timetable/', include(('fyt.timetable.urls', 'timetable'))),
    url(r'^training/', include(('fyt.training.urls', 'training'))),
    url(r'^users/', include(('fyt.users.urls', 'users'))),
    url(r'^volunteers/', include(('fyt.applications.urls', 'applications'))),
]

# Install django-debug-toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
