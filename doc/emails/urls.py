
from django.conf.urls import url

from doc.emails.views import EmailList

urlpatterns = [
    url(r'$', EmailList.as_view(), name='email_lists'),
]
