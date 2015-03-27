
from django.conf.urls import patterns, url

from doc.emails.views import EmailList

urlpatterns = patterns(
    '',
    url(r'$', EmailList.as_view(), name='email_lists'),
)
