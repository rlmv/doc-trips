

from django.conf.urls import patterns, include, url

from doc.webauth.views import login, logout

urlpatterns = patterns('', 
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
)
