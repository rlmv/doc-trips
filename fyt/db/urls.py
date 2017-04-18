from django.conf.urls import include, url

from fyt.applications.urls import (
    application_urlpatterns,
    grader_urlpatterns,
    score_urlpatterns,
)
from fyt.croos.urls import croo_urlpatterns
from fyt.db.views import (
    DatabaseLandingPage,
    MigrateForward,
    RedirectToCurrentDatabase,
)
from fyt.incoming.urls import registration_urlpatterns, trippee_urlpatterns
from fyt.training.urls import session_urlpatterns, attendee_urlpatterns
from fyt.transport.urls import (
    externalbus_urlpatterns,
    route_urlpatterns,
    scheduledtransport_urlpatterns,
    stop_urlpatterns,
    vehicle_urlpatterns,
)
from fyt.trips.urls import (
    campsite_urlpatterns,
    checklist_urlpatterns,
    foodbox_urlpatterns,
    leader_urlpatterns,
    packet_urlpatterns,
    section_urlpatterns,
    template_urlpatterns,
    trip_urlpatterns,
    triptype_urlpatterns,
)


"""
All database urlpatterns take a trips_year param.
"""

database_urlpatterns = [
    url(r'^$', DatabaseLandingPage.as_view(), name='landing_page'),
    url(r'^applications/',
        include(application_urlpatterns, namespace='volunteer')),
    url(r'^campsites/',
        include(campsite_urlpatterns, namespace='campsite')),
    url(r'^checklists/',
        include(checklist_urlpatterns, namespace='checklists')),
    url(r'^croos/',
        include(croo_urlpatterns, namespace='croo')),
    url(r'^emails/',
        include('fyt.emails.urls', namespace='emails')),
    url(r'^foodbox/',
        include(foodbox_urlpatterns, namespace='foodbox')),
    url(r'^grades/',
        include(grader_urlpatterns)),
    url(r'^incidents/',
        include('fyt.safety.urls', namespace='safety')),
    url(r'^leaders/',
        include(leader_urlpatterns)),
    url(r'^packets/',
        include(packet_urlpatterns, namespace='packets')),
    url(r'^raids/',
        include('fyt.raids.urls', namespace='raids')),
    url(r'^registrations/',
        include(registration_urlpatterns, namespace='registration')),
    url(r'^reports/',
        include('fyt.reports.urls', namespace='reports')),
    url(r'^routes/',
        include(route_urlpatterns, namespace='route')),
    url(r'^scores/',
        include(score_urlpatterns, namespace='score')),
    url(r'^sections/',
        include(section_urlpatterns, namespace='section')),
    url(r'^sessions/',
        include(session_urlpatterns, namespace='session')),
    url(r'^stops/',
        include(stop_urlpatterns, namespace='stop')),
    url(r'^templates/',
        include(template_urlpatterns, namespace='triptemplate')),
    url(r'^training/',
        include(attendee_urlpatterns, namespace='attendee')),
    url(r'^transport/external/',
        include(externalbus_urlpatterns, namespace='externalbus')),
    url(r'^transport/internal/',
        include(scheduledtransport_urlpatterns, namespace='scheduledtransport')),
    url(r'^trippees/',
        include(trippee_urlpatterns, namespace='incomingstudent')),
    url(r'^trips/',
        include(trip_urlpatterns, namespace='trip')),
    url(r'^types/',
        include(triptype_urlpatterns, namespace='triptype')),
    url(r'^vehicles/',
        include(vehicle_urlpatterns, namespace='vehicle')),
]

urlpatterns = [
    url(r'^$', RedirectToCurrentDatabase.as_view(), name='current'),
    url(r'^migrate/$', MigrateForward.as_view(), name='migrate'),
    # capture the 'trips_year' parameter
    url(r'^(?P<trips_year>[0-9]+)/', include(database_urlpatterns)),
]
