
from django.conf.urls import url

from doc.core.views import EditSettings

urlpatterns = [
    url(r'^settings$', EditSettings.as_view(), name='settings'),
]
