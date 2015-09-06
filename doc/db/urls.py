
from django.conf.urls import url, include

from doc.croos.urls import croo_urlpatterns
from doc.trips.urls import (
    trip_urlpatterns, template_urlpatterns, triptype_urlpatterns,
    campsite_urlpatterns, section_urlpatterns, leader_urlpatterns,
    foodbox_urlpatterns, packet_urlpatterns, checklist_urlpatterns
)
from doc.transport.urls import (
    scheduledtransport_urlpatterns, transportstop_urlpatterns,
    vehicle_urlpatterns, route_urlpatterns,
    externalbus_urlpatterns
)
from doc.applications.urls import (
    application_urlpatterns, grader_urlpatterns, grade_urlpatterns
)
from doc.incoming.urls import (
    trippee_urlpatterns, registration_urlpatterns, settings_urlpatterns)
from doc.db.views import DatabaseLandingPage, RedirectToCurrentDatabase

from doc.trips.views import TrippeeLeaderCounts
from doc.transport.views import (
    TransportChecklist, ExternalBusChecklist
)

"""
All database urlpatterns take a trips_year param.
"""
database_urlpatterns = [
    url(r'^$', DatabaseLandingPage.as_view(), name='landing_page'),
    url(r'^trips/', include(trip_urlpatterns)),
    url(r'^leaders/', include(leader_urlpatterns)),                    
    url(r'^templates/', include(template_urlpatterns)),
    url(r'^types/', include(triptype_urlpatterns)),
    url(r'^campsites/', include(campsite_urlpatterns)),
    url(r'^sections/', include(section_urlpatterns)),
    url(r'^croos/', include(croo_urlpatterns)),                        
    url(r'^stops/', include(transportstop_urlpatterns)),
    url(r'^routes/', include(route_urlpatterns)),
    url(r'^vehicles/', include(vehicle_urlpatterns)),
    url(r'^applications/', include(application_urlpatterns)),
    url(r'^grades/', include(grade_urlpatterns)),
    url(r'^graders/', include(grader_urlpatterns)),
    url(r'^trippees/', include(trippee_urlpatterns)),
    url(r'^registrations/', include(registration_urlpatterns)),
    url(r'^', include(settings_urlpatterns)),
    url(r'^transport/', include(scheduledtransport_urlpatterns)),
    url(r'^transport/external/', include(externalbus_urlpatterns)),
    url(r'^emails/', include('doc.emails.urls', namespace='emails')),
    url(r'^reports/', include('doc.reports.urls', namespace='reports')),
    url(r'^raids/', include('doc.raids.urls', namespace='raids')),
    url(r'^counts/people/', TrippeeLeaderCounts.as_view(), name='people_counts'),
    url(r'^checklists/external/(?P<route_pk>[0-9]+)/(?P<section_pk>[0-9]+)/$',
        ExternalBusChecklist.as_view(), name='external_checklist'),
    url(r'^foodbox/', include(foodbox_urlpatterns, namespace='foodbox')),
    url(r'^packets/', include(packet_urlpatterns, namespace='packets')),
    url(r'^incidents/', include('doc.safety.urls', namespace='safety')),
    url(r'^checklists/', include(checklist_urlpatterns, namespace='checklists')),
]

urlpatterns = [
    url(r'^$', RedirectToCurrentDatabase.as_view(), name='db_redirect'),
    # capture the 'trips_year' parameter which is passed to core views
    url(r'^(?P<trips_year>[0-9]+)/', include(database_urlpatterns)),
]
