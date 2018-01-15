from django.conf.urls import include, url

from fyt.applications.urls import (
    application_urlpatterns,
    grader_urlpatterns,
    score_urlpatterns,
)
from fyt.croos.urls import croo_urlpatterns
from fyt.core.views import (
    DatabaseLandingPage,
    MigrateForward,
    RedirectToCurrentDatabase,
)
from fyt.incoming.urls import registration_urlpatterns, trippee_urlpatterns
from fyt.training.urls import attendee_urlpatterns, session_urlpatterns
from fyt.transport.urls import (
    externalbus_urlpatterns,
    internalbus_urlpatterns,
    route_urlpatterns,
    stop_urlpatterns,
    transportconfig_urlpatterns,
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
        include((application_urlpatterns, 'volunteer'))),
    url(r'^campsites/',
        include((campsite_urlpatterns, 'campsite'))),
    url(r'^checklists/',
        include((checklist_urlpatterns, 'checklists'))),
    url(r'^croos/',
        include((croo_urlpatterns, 'croo'))),
    url(r'^emails/',
        include(('fyt.emails.urls', 'emails'))),
    url(r'^foodbox/',
        include((foodbox_urlpatterns, 'foodbox'))),
    url(r'^grades/',
        include((grader_urlpatterns))),
    url(r'^incidents/',
        include(('fyt.safety.urls', 'safety'))),
    url(r'^leaders/',
        include((leader_urlpatterns))),
    url(r'^packets/',
        include((packet_urlpatterns, 'packets'))),
    url(r'^raids/',
        include(('fyt.raids.urls', 'raids'))),
    url(r'^registrations/',
        include((registration_urlpatterns, 'registration'))),
    url(r'^reports/',
        include(('fyt.reports.urls', 'reports'))),
    url(r'^routes/',
        include((route_urlpatterns, 'route'))),
    url(r'^scores/',
        include((score_urlpatterns, 'score'))),
    url(r'^sections/',
        include((section_urlpatterns, 'section'))),
    url(r'^sessions/',
        include((session_urlpatterns, 'session'))),
    url(r'^stops/',
        include((stop_urlpatterns, 'stop'))),
    url(r'^templates/',
        include((template_urlpatterns, 'triptemplate'))),
    url(r'^training/',
        include((attendee_urlpatterns, 'attendee'))),
    url(r'^transport/',
        include((transportconfig_urlpatterns, 'transportconfig'))),
    url(r'^transport/external/',
        include((externalbus_urlpatterns, 'externalbus'))),
    url(r'^transport/internal/',
        include((internalbus_urlpatterns, 'internalbus'))),
    url(r'^trippees/',
        include((trippee_urlpatterns, 'incomingstudent'))),
    url(r'^trips/',
        include((trip_urlpatterns, 'trip'))),
    url(r'^types/',
        include((triptype_urlpatterns, 'triptype'))),
    url(r'^vehicles/',
        include((vehicle_urlpatterns, 'vehicle'))),
]

urlpatterns = [
    url(r'^$', RedirectToCurrentDatabase.as_view(), name='current'),
    url(r'^migrate/$', MigrateForward.as_view(), name='migrate'),
    # capture the 'trips_year' parameter
    url(r'^(?P<trips_year>[0-9]+)/', include(database_urlpatterns)),
]
