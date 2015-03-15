
from django.conf.urls import patterns, url

from doc.db.urlhelpers import DB_REGEX
from doc.trips.views import *
from doc.trips.views import (TripLeaderIndexView, UpdateLeaderWithAssignedTrip,
                             RemoveAssignedTrip)

"""
OOdles of urls. These patterns all included in the main 
database urlpatterns.
"""

trip_urlpatterns = patterns('', 
    url(DB_REGEX['LIST'], ScheduledTripListView.as_view(), name='scheduledtrip_index'),
    url(DB_REGEX['CREATE'], ScheduledTripCreateView.as_view(), name='scheduledtrip_create'),
    url(DB_REGEX['DETAIL'], ScheduledTripDetailView.as_view(), name='scheduledtrip_detail'),                            
    url(DB_REGEX['UPDATE'], ScheduledTripUpdateView.as_view(), name='scheduledtrip_update'),
    url(DB_REGEX['DELETE'], ScheduledTripDeleteView.as_view(), name='scheduledtrip_delete'),                            
)

template_urlpatterns = patterns('',
    url(DB_REGEX['LIST'], TripTemplateListView.as_view(), name='triptemplate_index'),
    url(DB_REGEX['CREATE'], TripTemplateCreateView.as_view(), name='triptemplate_create'),
    url(DB_REGEX['DETAIL'], TripTemplateDetailView.as_view(), name='triptemplate_detail'),
    url(DB_REGEX['UPDATE'], TripTemplateUpdateView.as_view(), name='triptemplate_update'),
    url(DB_REGEX['DELETE'], TripTemplateDeleteView.as_view(), name='triptemplate_delete'),
)                                

triptype_urlpatterns = patterns('',
    url(DB_REGEX['LIST'], TripTypeListView.as_view(), name='triptype_index'),                
    url(DB_REGEX['CREATE'], TripTypeCreateView.as_view(), name='triptype_create'),
    url(DB_REGEX['DETAIL'], TripTypeDetailView.as_view(), name='triptype_detail'),
    url(DB_REGEX['UPDATE'], TripTypeUpdateView.as_view(), name='triptype_update'),
    url(DB_REGEX['DELETE'], TripTypeDeleteView.as_view(), name='triptype_delete'),
)                                

campsite_urlpatterns = patterns('',
    url(DB_REGEX['LIST'], CampsiteListView.as_view(), name='campsite_index'),
    url(DB_REGEX['CREATE'], CampsiteCreateView.as_view(), name='campsite_create'),     
    url(DB_REGEX['DETAIL'], CampsiteDetailView.as_view(), name='campsite_detail'),                      
    url(DB_REGEX['UPDATE'], CampsiteUpdateView.as_view(), name='campsite_update'),                          
    url(DB_REGEX['DELETE'], CampsiteDeleteView.as_view(), name='campsite_delete'),                      
)                                

section_urlpatterns = patterns(
    '',
    url(DB_REGEX['LIST'], SectionListView.as_view(), name='section_index'),
    url(DB_REGEX['CREATE'], SectionCreateView.as_view(), name='section_create'),                      
url(DB_REGEX['DETAIL'], SectionDetailView.as_view(), name='section_detail'),                         
    url(DB_REGEX['UPDATE'], SectionUpdateView.as_view(), name='section_update'),                            
    url(DB_REGEX['DELETE'], SectionDeleteView.as_view(), name='section_delete'),                      
)                                

leader_urlpatterns = patterns(
    '', 
    url(r'^$', TripLeaderIndexView.as_view(), name='leader_index'),
    url(r'^assign/(?P<trip>[0-9]+)$', AssignTripLeaderView.as_view(), name='assign_leader'),
    url(r'^assign/post/(?P<leader_pk>[0-9]+)$', 
        UpdateLeaderWithAssignedTrip.as_view(), name='assign_leader_to_trip'),
    url(r'^remove/(?P<leader_pk>[0-9]+)$', 
        RemoveAssignedTrip.as_view(), name='remove_leader_from_trip'),
)
                              

