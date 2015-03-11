
from django.conf.urls import patterns, url, include

from doc.trippees.views import Register, EditRegistration, ViewRegistration

urlpatterns = patterns(
    '',
    url(r'^register/$', Register.as_view(), name='register'),
    url(r'^register/edit/$', EditRegistration.as_view(), name='edit_registration'),
    url(r'^register/view/$', ViewRegistration.as_view(), name='view_registration'),
)


trippee_urlpatterns = patterns(
    '',
)
                            
