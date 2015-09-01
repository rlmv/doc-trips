

from django.conf.urls import include, url

from doc.webauth.views import login, logout
from doc.users.views import UpdateEmail

urlpatterns = [
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^email/$', UpdateEmail.as_view(), name='update_email'),
]
