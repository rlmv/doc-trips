

from django.conf.urls import patterns, url, include

trips_year_urlpatterns = patterns('', 
    url(r'^trips/', include('trip.urls', namespace='trip')),
)

urlpatterns = patterns('',
    # capture the 'trips_year' parameter which is passed to all db views                 
    url(r'^(?P<trips_year>[0-9]+)/', include(trips_year_urlpatterns)),
)                       
                                  

   
