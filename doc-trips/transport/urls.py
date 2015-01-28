

from django.conf.urls import patterns, url

from db.urlhelpers import DB_REGEX

from transport.views import *

transportstop_urlpatterns = patterns('', 
    url(DB_REGEX['LIST'], StopListView.as_view(), name='stop_index'),
    url(DB_REGEX['CREATE'], StopCreateView.as_view(), name='stop_create'),
    url(DB_REGEX['DETAIL'], StopDetailView.as_view(), name='stop_detail'),
    url(DB_REGEX['UPDATE'], StopUpdateView.as_view(), name='stop_update'),
    url(DB_REGEX['DELETE'], StopDeleteView.as_view(), name='stop_delete'),
)                                 
