
from django.conf.urls import patterns, url, include

from doc.trippees.views import (Register, EditRegistration, ViewRegistration, 
                                RegistrationNotAvailable)

urlpatterns = patterns(
    '',
    url(r'^register/$', Register.as_view(), name='register'),
    url(r'^register/edit/$', EditRegistration.as_view(), name='edit_registration'),
    url(r'^register/view/$', ViewRegistration.as_view(), name='view_registration'),
    url(r'^register/not-available/$', RegistrationNotAvailable.as_view(), name='registration_not_available'),
)


trippee_urlpatterns = patterns(
    '',
)
                            
