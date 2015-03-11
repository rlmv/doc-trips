
from django.conf.urls import patterns, url, include

from doc.trippees.views import Register, EditRegistration

urlpatterns = patterns(
    '',
    url(r'^register/$', Register.as_view(), name='register')
    url(r'^register/edit/$', EditRegistration.as_view(), name='edit_registration'),
)


trippee_urlpatterns = patterns(
    '',
)
                            
