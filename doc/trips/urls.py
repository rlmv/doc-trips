from django.conf.urls import patterns, url

from doc.db.urlhelpers import DB_REGEX
from doc.trips.views import *

"""
OOdles of urls. These patterns all included in the main
database urlpatterns.
"""

trip_urlpatterns = [
    url(DB_REGEX['LIST'], TripList.as_view(), name='trip_index'),
    url(DB_REGEX['CREATE'], TripCreate.as_view(), name='trip_create'),
    url(DB_REGEX['DETAIL'], TripDetail.as_view(), name='trip_detail'),
    url(DB_REGEX['UPDATE'], TripUpdate.as_view(), name='trip_update'),
    url(DB_REGEX['DELETE'], TripDelete.as_view(), name='trip_delete'),
]

template_urlpatterns = [
    url(DB_REGEX['LIST'], TripTemplateList.as_view(),
        name='triptemplate_index'),
    url(DB_REGEX['CREATE'], TripTemplateCreate.as_view(),
        name='triptemplate_create'),
    url(DB_REGEX['DETAIL'], TripTemplateDetail.as_view(),
        name='triptemplate_detail'),
    url(DB_REGEX['UPDATE'], TripTemplateUpdate.as_view(),
        name='triptemplate_update'),
    url(DB_REGEX['DELETE'], TripTemplateDelete.as_view(),
        name='triptemplate_delete'),
]

triptype_urlpatterns = [
    url(DB_REGEX['LIST'], TripTypeList.as_view(),
        name='triptype_index'),   
    url(DB_REGEX['CREATE'], TripTypeCreate.as_view(),
        name='triptype_create'),
    url(DB_REGEX['DETAIL'], TripTypeDetail.as_view(),
        name='triptype_detail'),
    url(DB_REGEX['UPDATE'], TripTypeUpdate.as_view(),
        name='triptype_update'),
    url(DB_REGEX['DELETE'], TripTypeDelete.as_view(),
        name='triptype_delete'),
]

campsite_urlpatterns = [
    url(DB_REGEX['LIST'], CampsiteList.as_view(),
        name='campsite_index'),
    url(DB_REGEX['CREATE'], CampsiteCreate.as_view(),
        name='campsite_create'),
    url(DB_REGEX['DETAIL'], CampsiteDetail.as_view(),
        name='campsite_detail'),
    url(DB_REGEX['UPDATE'], CampsiteUpdate.as_view(),
        name='campsite_update'),
    url(DB_REGEX['DELETE'], CampsiteDelete.as_view(),
        name='campsite_delete'),
]

section_urlpatterns = [
    url(DB_REGEX['LIST'], SectionList.as_view(),
        name='section_index'),
    url(DB_REGEX['CREATE'], SectionCreate.as_view(),
        name='section_create'),
    url(DB_REGEX['DETAIL'], SectionDetail.as_view(),
        name='section_detail'),
    url(DB_REGEX['UPDATE'], SectionUpdate.as_view(),
        name='section_update'),
    url(DB_REGEX['DELETE'], SectionDelete.as_view(),
        name='section_delete'),
]

leader_urlpatterns = [
    url(r'^$', LeaderTrippeeIndexView.as_view(), name='leader_index'),
    url(r'^assign/trippee/(?P<trip_pk>[0-9]+)$', 
        AssignTrippee.as_view(), name='assign_trippee'),
    url(r'^assign/trippee/(?P<trippee_pk>[0-9]+)/update/$', 
        AssignTrippeeToTrip.as_view(), name='assign_trippee_to_trip'),
    url(r'^assign/leader/(?P<trip_pk>[0-9]+)$',
        AssignTripLeaderView.as_view(), name='assign_leader'),
    url(r'^assign/leader/(?P<leader_pk>[0-9]+)/update/$',
        AssignLeaderToTrip.as_view(), name='assign_leader_to_trip'),
    url(r'^remove/leader/(?P<leader_pk>[0-9]+)$',
        RemoveAssignedTrip.as_view(), name='remove_leader_from_trip'),
]

foodbox_urlpatterns = [
    url(r'^rules/$', FoodboxRules.as_view(), name='rules'),
    url(r'^counts/$', FoodboxCounts.as_view(), name='counts'),
]

packet_urlpatterns = [
    url(r'^for/trip/(?P<pk>[0-9]+)/$', LeaderPacket.as_view(), name='trip'),
    url(r'^for/section/(?P<section_pk>[0-9]+)/$',
        PacketsForSection.as_view(), name='section'),
    url(r'^medical/for/section/(?P<section_pk>[0-9]+)/$',
        MedicalInfoForSection.as_view(), name='medical'),
]

checklist_urlpatterns = [
    url(r'^$', Checklists.as_view(), name='all'),
]
