from django.conf.urls import patterns, include, url

# default Django admin interface
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^user/', include('user.urls', namespace='user')),
    url(r'^db/', include('db.urls', namespace='db')),
    url(r'^leader/', include('leader.urls', namespace='leader')),
    url(r'^admin/', include(admin.site.urls)),
)
