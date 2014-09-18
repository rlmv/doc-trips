
from django.conf.urls import patterns, url

from trip.views import *

trip_urlpatterns = patterns('', 
    ScheduledTripListView.urlpattern(),
    ScheduledTripCreateView.urlpattern(),                            
    ScheduledTripUpdateView.urlpattern(),                            
    ScheduledTripDeleteView.urlpattern(),                        
)

template_urlpatterns = patterns('',
    TripTemplateListView.urlpattern(),
    TripTemplateCreateView.urlpattern(),                            
    TripTemplateUpdateView.urlpattern(),                            
    TripTemplateDeleteView.urlpattern(),                        
)                                

triptype_urlpatterns = patterns('',
    TripTypeListView.urlpattern(),
    TripTypeCreateView.urlpattern(),                            
    TripTypeDetailView.urlpattern(),                            
    TripTypeUpdateView.urlpattern(),                            
    TripTypeDeleteView.urlpattern(),                        
)                                

campsite_urlpatterns = patterns('',
    CampsiteListView.urlpattern(),
    CampsiteCreateView.urlpattern(),                            
    CampsiteUpdateView.urlpattern(),                            
    CampsiteDeleteView.urlpattern(),                        
)                                

section_urlpatterns = patterns('',
    SectionListView.urlpattern(),
    SectionCreateView.urlpattern(),                        
    SectionDetailView.urlpattern(),                           
    SectionUpdateView.urlpattern(),                            
    SectionDeleteView.urlpattern(),                        
)                                

