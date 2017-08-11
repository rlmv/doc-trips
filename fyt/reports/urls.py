from django.conf.urls import url

from fyt.reports.views import *


urlpatterns = [
    url(r'^applications/all/$', VolunteerCSV.as_view(), name='all_apps'),
    url(r'^applications/leaders/$', TripLeadersCSV.as_view(),
        name='leaders'),
    url(r'^applications/croo-members/$', CrooMembersCSV.as_view(),
        name='croo_members'),
    url(r'^dietary/$', DietaryRestrictions.as_view(), name='dietary'),
    url(r'^registrations/financial-aid/$', FinancialAidCSV.as_view(),
        name='financial_aid'),
    url(r'^incoming/trippees/$', TrippeesCSV.as_view(), name='trippees'),
    url(r'^incoming/charges/$', Charges.as_view(), name="charges"),
    url(r'^incoming/housing/$', Housing.as_view(), name="housing"),
    url(r'^registrations/$', Registrations.as_view(), name="registrations"),
    url(r'^registrations/medical/$', MedicalInfo.as_view(), name="medical"),
    url(r'^registrations/doc-members/$', DocMembers.as_view(), name="doc_members"),
    url(r'^registrations/feelings/$', Feelings.as_view(), name="feelings"),
    url(r'^transport/external/requests/$', ExternalBusRequestsCSV.as_view(),
        name='bus_stops'),
    url(r'^transport/external/riders/(?P<bus_pk>[0-9]+)/$',
        ExternalBusRidersCSV.as_view(), name='bus_riders'),
    url(r'^tshirts/$', TShirts.as_view(), name='tshirts'),
    url(r'^foodboxes/$', Foodboxes.as_view(), name='foodboxes'),
    url(r'^statistics/$', Statistics.as_view(), name='statistics'),
]
