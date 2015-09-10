from django.conf.urls import url

from fyt.raids.views import *

urlpatterns = [
    url(r'^$', RaidHome.as_view(), name='home'),
    url(r'^all/$', RaidList.as_view(), name='list'),
    url(r'^trips/$', TripsToRaid.as_view(), name='trips'),
    url(r'^create/$', RaidTrip.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/detail/$', RaidDetail.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/delete/$', RaidDelete.as_view(), name='delete'),
    url(r'^info/$', UpdateRaidInfo.as_view(), name='info'),
]
