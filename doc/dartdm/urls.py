from django.conf.urls import patterns, url

from doc.dartdm.views import dartdm_lookup_view

urlpatterns = patterns('', 
    url(r'^lookup/$', dartdm_lookup_view, name='lookup'),     
)

