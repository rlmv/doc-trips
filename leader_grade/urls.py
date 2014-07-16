

from django.conf.urls import url, patterns
from .views import *


urlpatterns = patterns('', 
    url(r'^$', redirect_to_next_gradable_application, name='random'),
    url(r'^(?P<pk>[0-9]+)$', grade_application, name='grade'),
)
