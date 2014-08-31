

from django.conf.urls import patterns, url, include

from trip.urls import * # TODO
from leader.urls import *

database_urlpatterns = patterns('', 
    url(r'^trips/', include(trip_urlpatterns, namespace='trip')),
    url(r'^templates/', include(template_urlpatterns, namespace='template')),                              
    url(r'^types/', include(triptype_urlpatterns, namespace='triptype')),                              
    url(r'^campsites/', include(campsite_urlpatterns, namespace='campsite')),
    url(r'^sections/', include(section_urlpatterns, namespace='section')),                                  
    url(r'^leaders/', include(leader_urlpatterns, namespace='leaders')),                            
)

urlpatterns = patterns('',
    # capture the 'trips_year' parameter which is passed to all db views                 
    url(r'^(?P<trips_year>[0-9]+)/', include(database_urlpatterns)),
)                       
                                  

   
