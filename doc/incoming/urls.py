
from django.conf.urls import url, include

from doc.db.urlhelpers import DB_REGEX
from doc.incoming.views import (
    Register, EditRegistration,
    RegistrationNotAvailable, IncomingStudentPortal,
    RegistrationIndexView, RegistrationDetailView,
    RegistrationUpdateView, RegistrationDeleteView,
    IncomingStudentIndexView, IncomingStudentDeleteView,
    IncomingStudentDetailView, IncomingStudentUpdateView,
    UpdateTripAssignmentView,
    UploadIncomingStudentData,
    MatchRegistrations
)

urlpatterns = [
    url(r'^$', IncomingStudentPortal.as_view(), name='portal'),
    url(r'^register/$', Register.as_view(), name='register'),
    url(r'^register/edit/$', EditRegistration.as_view(), name='edit_registration'),
    url(r'^register/not-available/$', RegistrationNotAvailable.as_view(), name='registration_not_available'),
]


# ---- database urlpatterns ------

trippee_urlpatterns = [
    url(DB_REGEX['LIST'], IncomingStudentIndexView.as_view(), name='incomingstudent_index'),
    url(DB_REGEX['DETAIL'], IncomingStudentDetailView.as_view(), name='incomingstudent_detail'),
    url(DB_REGEX['UPDATE'], IncomingStudentUpdateView.as_view(), name='incomingstudent_update'),
    url(DB_REGEX['DELETE'], IncomingStudentDeleteView.as_view(), name='incomingstudent_delete'),

    url(r'^(?P<pk>[0-9]+)/update/assignment$', UpdateTripAssignmentView.as_view(),
        name='incomingstudent_update_assignment'),
    url(r'^upload/$', UploadIncomingStudentData.as_view(), name='upload_incoming'),
]

registration_urlpatterns = [
    url(DB_REGEX['LIST'], RegistrationIndexView.as_view(),
        name='registration_index'),
    url(DB_REGEX['DETAIL'], RegistrationDetailView.as_view(),
        name='registration_detail'),
    url(DB_REGEX['UPDATE'], RegistrationUpdateView.as_view(),
        name='registration_update'),
    url(DB_REGEX['DELETE'], RegistrationDeleteView.as_view(),
        name='registration_delete'),
    url(r'^match/$', MatchRegistrations.as_view(), name='registration_match'),
]
