

from django.conf.urls import patterns, url

from trip.views import *

urlpatterns = patterns('', 
    url(r'^$', ScheduledTripListView.as_view(), name='trip_index'),
    url(r'^update/(?P<pk>[0-9]+)', ScheduledTripUpdateView.as_view(), name='trip_update'),
    url(r'^create$', ScheduledTripCreateView.as_view(), name='trip_create'),                   
)

