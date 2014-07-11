from django.conf.urls import patterns, include, url

# default Django admin interface
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'views.index', name='index'),
    url(r'^user/', include('user.urls', namespace='user')),
    url(r'^admin/', include(admin.site.urls)),
)
