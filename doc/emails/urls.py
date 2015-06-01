
from django.conf.urls import url

from doc.emails.views import Applicants, LeadersByTripType, LeadersBySection

urlpatterns = [
    url(r'^applicants/$', Applicants.as_view(), name='applicants'),
    url(r'^leaders/by-triptype/$', LeadersByTripType.as_view(), name='leaders_by_triptype'),
    url(r'^leaders/by-section/$', LeadersBySection.as_view(), name='leaders_by_section'),
    
]
