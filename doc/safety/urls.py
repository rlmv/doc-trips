
from django.conf.urls import url, include

from doc.db.urlhelpers import DB_REGEX
from doc.safety.views import *

urlpatterns = [
    url(r'^new/$', NewIncident.as_view(), name='create'),
    url(DB_REGEX['DETAIL'], IncidentDetail.as_view(), name='detail'),
]
