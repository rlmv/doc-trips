from django.conf.urls import url

from fyt.core.urlhelpers import DB_REGEX
from fyt.croos.views import (
    CrooCreateView,
    CrooDeleteView,
    CrooDetailView,
    CrooListView,
    CrooUpdateView,
)


croo_urlpatterns = [
    url(DB_REGEX['LIST'], CrooListView.as_view(), name='index'),
    url(DB_REGEX['CREATE'], CrooCreateView.as_view(), name='create'),
    url(DB_REGEX['UPDATE'], CrooUpdateView.as_view(), name='update'),
    url(DB_REGEX['DETAIL'], CrooDetailView.as_view(), name='detail'),
    url(DB_REGEX['DELETE'], CrooDeleteView.as_view(), name='delete'),
]
