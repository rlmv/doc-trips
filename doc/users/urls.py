

from django.conf.urls import patterns, include, url

urlpatterns = patterns('', 
    url(r'^login/$', 'webauth.views.login', name='login'),
    url(r'^logout/$', 'webauth.views.logout', name='logout'),
)
