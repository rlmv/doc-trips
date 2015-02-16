
from django.conf.urls import patterns, url

from db.urlhelpers import DB_REGEX
from applications.views import NewApplication

urlpatterns = patterns(
    '',
    url(r'^apply/$', NewApplication.as_view(), name='apply'),
)
