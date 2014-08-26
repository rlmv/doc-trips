

from django.conf.urls import patterns, url, include

from trip.urls import * # TODO

trips_year_urlpatterns = patterns('', 
    url(r'^trips/', include(trip_urlpatterns, namespace='trip')),
    url(r'^templates/', include(template_urlpatterns, namespace='template')),                              
    url(r'^types/', include(triptype_urlpatterns, namespace='triptype')),                              
)

urlpatterns = patterns('',
    # capture the 'trips_year' parameter which is passed to all db views                 
    url(r'^(?P<trips_year>[0-9]+)/', include(trips_year_urlpatterns)),
)                       
                                  

   
