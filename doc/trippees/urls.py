
from django.conf.urls import patterns, url, include

from doc.db.urlhelpers import DB_REGEX
from doc.trippees.views import (Register, EditRegistration, ViewRegistration, 
                                RegistrationNotAvailable,
                                RegistrationIndexView,
                                IncomingStudentIndexView, IncomingStudentDetailView, 
                                IncomingStudentUpdateView,
                                UploadIncomingStudentData)

urlpatterns = patterns(
    '',
    url(r'^register/$', Register.as_view(), name='register'),
    url(r'^register/edit/$', EditRegistration.as_view(), name='edit_registration'),
    url(r'^register/view/$', ViewRegistration.as_view(), name='view_registration'),
    url(r'^register/not-available/$', RegistrationNotAvailable.as_view(), name='registration_not_available'),
)


# ---- database urlpatterns ------

trippee_urlpatterns = patterns(
    '',
    url(DB_REGEX['LIST'], IncomingStudentIndexView.as_view(), name='trippee_index'),
    url(DB_REGEX['DETAIL'], IncomingStudentDetailView.as_view(), name='trippee_detail'),
    url(DB_REGEX['UPDATE'], IncomingStudentUpdateView.as_view(), name='trippee_update'),
    url(r'^upload/$', UploadIncomingStudentData.as_view(), name='upload_incoming'),
)

registration_urlpatterns = patterns(
    '',
    url(DB_REGEX['LIST'], RegistrationIndexView.as_view(), name='registration_index'),

)
                            
