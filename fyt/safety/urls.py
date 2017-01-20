from django.conf.urls import url

from fyt.db.urlhelpers import DB_REGEX
from fyt.safety.views import *


urlpatterns = [
    url(r'^$', IncidentList.as_view(), name='list'),
    url(r'^new/$', NewIncident.as_view(), name='create'),
    url(DB_REGEX['DETAIL'], IncidentDetail.as_view(), name='detail'),
    url(DB_REGEX['DELETE'], DeleteIncident.as_view(), name='delete'),
    url(DB_REGEX['UPDATE'], UpdateIncident.as_view(), name='update'),
]
