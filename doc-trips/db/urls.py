

from django.conf.urls import patterns, url, include

from trip.urls import * # TODO
from leader.urls import *

database_urlpatterns = patterns('', 
    url(r'^trips/', include(trip_urlpatterns)),
    url(r'^templates/', include(template_urlpatterns)),
    url(r'^types/', include(triptype_urlpatterns)),
    url(r'^campsites/', include(campsite_urlpatterns)),
    url(r'^sections/', include(section_urlpatterns)),
    url(r'^leaders/', include(leaderapplication_urlpatterns)),
)

urlpatterns = patterns('',
    # capture the 'trips_year' parameter which is passed to all db views                 
    url(r'^(?P<trips_year>[0-9]+)/', include(database_urlpatterns)),
)                       
                                  

   
