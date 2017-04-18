
from django.conf.urls import url

from fyt.db.urlhelpers import DB_REGEX
from fyt.training.views import (
    AttendeeUpdate,
    NewSession,
    RecordAttendance,
    SessionDelete,
    SessionDetail,
    SessionList,
    SessionUpdate,
    Signup,
)


# Backend database views
session_urlpatterns = [
    url(DB_REGEX['LIST'], SessionList.as_view(), name='index'),
    url(DB_REGEX['CREATE'], NewSession.as_view(), name='create'),
    url(DB_REGEX['DETAIL'], SessionDetail.as_view(), name='detail'),
    url(DB_REGEX['UPDATE'], SessionUpdate.as_view(), name='update'),
    url(DB_REGEX['DELETE'], SessionDelete.as_view(), name='delete'),
    url(r'^(?P<pk>[0-9]+)/update/attendance', RecordAttendance.as_view(),
        name='update_attendance'),
]

attendee_urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/update/$', AttendeeUpdate.as_view(), name='update'),
]

# Public-facing views
urlpatterns = [
    url(r'^$', Signup.as_view(), name='signup'),
]
