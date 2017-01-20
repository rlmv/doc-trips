

from django.conf.urls import url

from fyt.users.views import UpdateEmail
from fyt.webauth.views import login, logout


urlpatterns = [
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^email/$', UpdateEmail.as_view(), name='update_email'),
]
