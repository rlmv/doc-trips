from django.conf.urls import url

from .views import *

from fyt.core.urlhelpers import DB_REGEX


urlpatterns = [
    url(r'^$', IncomingStudentPortal.as_view(), name='portal'),
    url(r'^register/$', Register.as_view(), name='register'),
    url(r'^register/edit/$', EditRegistration.as_view(), name='edit_registration'),
    url(
        r'^register/not-available/$',
        RegistrationNotAvailable.as_view(),
        name='registration_not_available',
    ),
]

# ---- database urlpatterns ------

trippee_urlpatterns = [
    url(DB_REGEX['LIST'], IncomingStudentIndex.as_view(), name='index'),
    url(DB_REGEX['DETAIL'], IncomingStudentDetail.as_view(), name='detail'),
    url(DB_REGEX['UPDATE'], IncomingStudentUpdate.as_view(), name='update'),
    url(DB_REGEX['DELETE'], IncomingStudentDelete.as_view(), name='delete'),
    url(
        r'^(?P<pk>[0-9]+)/update/assignment$',
        UpdateTripAssignment.as_view(),
        name='update_assignment',
    ),
    url(r'^upload/$', UploadIncomingStudentData.as_view(), name='upload'),
    url(r'^upload/hb$', UploadHinmanBoxes.as_view(), name='upload_hb'),
]

registration_urlpatterns = [
    url(DB_REGEX['LIST'], RegistrationIndex.as_view(), name='index'),
    url(DB_REGEX['DETAIL'], RegistrationDetail.as_view(), name='detail'),
    url(DB_REGEX['UPDATE'], RegistrationUpdate.as_view(), name='update'),
    url(DB_REGEX['DELETE'], RegistrationDelete.as_view(), name='delete'),
    url(r'^create/non-student/$', NonStudentRegistration.as_view(), name='nonstudent'),
    url(r'^match/$', MatchRegistrations.as_view(), name='match'),
]

settings_urlpatterns = [url(r'^$', EditSettings.as_view(), name='settings')]
