from django.conf.urls import patterns, include, url

# default Django admin interface
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'views.index', name='index'),
    url(r'^user/', include('user.urls', namespace='user')),
    url(r'^leader/', include('leader.urls', namespace='leader')),
    url(r'^leader/grade/', include('leader_grade.urls', namespace='grade')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
)
