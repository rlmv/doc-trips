

from django.conf.urls import include, url

from doc.webauth.views import login, logout

urlpatterns = [
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
]
