
from django.conf.urls import url

from fyt.emails.views import (
    Applicants,
    IncomingStudents,
    LeadersBySection,
    LeadersByTripType,
    Trippees,
)


urlpatterns = [
    url(r'^applicants/$', Applicants.as_view(), name='applicants'),
    url(r'^leaders/by-triptype/$', LeadersByTripType.as_view(), name='leaders_by_triptype'),
    url(r'^leaders/by-section/$', LeadersBySection.as_view(), name='leaders_by_section'),
    url(r'^incoming/$', IncomingStudents.as_view(), name='incoming'),
    url(r'^trippees/$', Trippees.as_view(), name='trippees'),

]
