
from django.conf.urls import patterns, url, include

from db.urlhelpers import DB_REGEX
from applications.views import (NewApplication, ContinueApplication, SetupApplication,
                                ApplicationDatabaseListView, 
                                LeaderApplicationDatabaseListView, 
                                LeaderApplicationDatabaseDetailView, 
                                LeaderApplicationDatabaseUpdateView)

urlpatterns = patterns(
    '',
    url(r'^apply/$', NewApplication.as_view(), name='apply'),
    url(r'^continue/$', ContinueApplication.as_view(), name='continue'),
    url(r'^setup/$', SetupApplication.as_view(), name='setup'),
)

# TODO: fix leaderapplication, leadersupplement mismatch

_leaderapplication_urlpatterns = patterns(
    '',
    url(DB_REGEX['LIST'], LeaderApplicationDatabaseListView.as_view(), name='leaderapplication_index'),
    url(DB_REGEX['DETAIL'], LeaderApplicationDatabaseDetailView.as_view(), name='leadersupplement_detail'),
    url(DB_REGEX['UPDATE'], LeaderApplicationDatabaseUpdateView.as_view(), name='leadersupplement_update'),
)

application_urlpatterns = patterns(
    '',
    url(DB_REGEX['LIST'], ApplicationDatabaseListView.as_view(), name='application_index'),
    url(r'^leaders/', include(_leaderapplication_urlpatterns)),
)

