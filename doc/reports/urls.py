from django.conf.urls import url

from doc.reports.views import (
    VolunteerCSV, TripLeaderApplicationsCSV, CrooApplicationsCSV
)

urlpatterns = [
    url(r'^applications/all/$', VolunteerCSV.as_view(), name='all_apps'),
    url(r'^applications/trip-leaders/$', TripLeaderApplicationsCSV.as_view(), 
        name='trip_leader_apps'),
    url(r'^applications/croos/$', CrooApplicationsCSV.as_view(),
        name='croo_apps'),
]
