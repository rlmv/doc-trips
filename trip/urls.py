

from django.conf.urls import patterns, url

from trip.views import *

urlpatterns = patterns('', 
    url(r'^$', ScheduledTripListView.as_view(), name='trip_index'),
    url(r'^create$', ScheduledTripCreateView.as_view(), name='trip_create'),                   
    url(r'^(?P<pk>[0-9]+)/update', ScheduledTripUpdateView.as_view(), name='trip_update'),
    url(r'^(?P<pk>[0-9]+)/delete', ScheduledTripDeleteView.as_view(), name='trip_delete'),
)

