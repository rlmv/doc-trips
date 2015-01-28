

from django.conf.urls import patterns, url, include

from trips.urls import (trip_urlpatterns, template_urlpatterns, triptype_urlpatterns, 
                        campsite_urlpatterns, section_urlpatterns)
from leaders.urls import leaderapplication_urlpatterns
from transport.urls import transportstop_urlpatterns
from db.views import DatabaseIndexView, RedirectToCurrentDatabase

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
    url(r'^transport/', include(transportstop_urlpatterns)),
)

urlpatterns = patterns('',
    url(r'^$', RedirectToCurrentDatabase.as_view(), name='db_redirect'),
    # capture the 'trips_year' parameter which is passed to all db views           
    url(r'^(?P<trips_year>[0-9]+)/', include(database_urlpatterns)),
)
