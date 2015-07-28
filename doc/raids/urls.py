from django.conf.urls import url

from doc.raids.views import *

urlpatterns = [
    url(r'^trips/$', TripsToRaid.as_view(), name='trips'),
    url(r'^create/$', RaidTrip.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/detail/$', RaidDetail.as_view(), name='detail'),
]
