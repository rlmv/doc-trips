

from django.conf.urls import patterns, url, include

from doc.trips.urls import (trip_urlpatterns, template_urlpatterns, triptype_urlpatterns, 
                        campsite_urlpatterns, section_urlpatterns)
from leaders.urls import leaderapplication_urlpatterns
from doc.croos.urls import crooapplication_urlpatterns, croo_urlpatterns
from doc.transport.urls import (transportstop_urlpatterns, route_urlpatterns, 
                            vehicle_urlpatterns)
from doc.db.views import DatabaseIndexView, RedirectToCurrentDatabase
from doc.applications.urls import application_urlpatterns

"""
All database urlpatterns take a trips_year param.
"""
database_urlpatterns = patterns('', 
    url(r'^$', DatabaseIndexView.as_view(), name='db_index'),
    url(r'^trips/', include(trip_urlpatterns)),
    url(r'^templates/', include(template_urlpatterns)),
    url(r'^types/', include(triptype_urlpatterns)),
    url(r'^campsites/', include(campsite_urlpatterns)),
    url(r'^sections/', include(section_urlpatterns)),
    url(r'^leaders/', include(leaderapplication_urlpatterns)),
    url(r'^croosapplications/', include(crooapplication_urlpatterns)),
    url(r'^croos/', include(croo_urlpatterns)),                            
    url(r'^stops/', include(transportstop_urlpatterns)),
    url(r'^routes/', include(route_urlpatterns)),
    url(r'^vehicles/', include(vehicle_urlpatterns)),                            
    url(r'^applications/', include(application_urlpatterns)),
)

urlpatterns = patterns('',
    url(r'^$', RedirectToCurrentDatabase.as_view(), name='db_redirect'),
    # capture the 'trips_year' parameter which is passed to all db views           
    url(r'^(?P<trips_year>[0-9]+)/', include(database_urlpatterns)),
)
