from django.conf.urls import url

from doc.dartdm.views import dartdm_lookup_view

urlpatterns = [
    url(r'^lookup/$', dartdm_lookup_view, name='lookup'),     
]

