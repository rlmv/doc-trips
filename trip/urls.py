

from django.conf.urls import patterns, url

from trip.views import *

urlpatterns = patterns('', 
    url(r'^$', trip_index, name='trip_index'),
)
