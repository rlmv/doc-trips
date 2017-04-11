
from django.conf.urls import url

from fyt.training.views import (
    NewSession,
    SessionList,
)

# Backend database views
session_urlpatterns = [
    url(r'^$', SessionList.as_view(), name='list'),
    url(r'^new/$', NewSession.as_view(), name='create'),
]
