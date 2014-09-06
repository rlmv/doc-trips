from django.conf.urls import patterns, url

from dartdm.views import dartdm_lookup_view

urlpatterns = patterns('', 
    url(r'^lookup/$', dartdm_lookup_view, name='lookup'),     
)

