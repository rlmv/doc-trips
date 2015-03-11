
from django.conf.urls import patterns, url, include

from doc.db.urlhelpers import DB_REGEX
from doc.croos.views import (CrooListView, CrooCreateView, CrooUpdateView, 
                             CrooDetailView, CrooDeleteView)

croo_urlpatterns = patterns(
    '',
    url(DB_REGEX['LIST'], CrooListView.as_view(), name='croo_index'),
    url(DB_REGEX['CREATE'], CrooCreateView.as_view(), name='croo_create'),
    url(DB_REGEX['UPDATE'], CrooUpdateView.as_view(), name='croo_update'),
    url(DB_REGEX['DETAIL'], CrooDetailView.as_view(), name='croo_detail'),
    url(DB_REGEX['DELETE'], CrooDeleteView.as_view(), name='croo_delete')
)
                        
