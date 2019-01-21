from django.conf.urls import url

from fyt.permissions.views import SetPermissions


urlpatterns = [url(r'^set/$', SetPermissions.as_view(), name='set_permissions')]
