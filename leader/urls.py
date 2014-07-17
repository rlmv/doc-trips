
from django.conf.urls import patterns, url

from .views import *

urlpatterns = patterns('', 
    url(r'^$', list_view, name='list'),
    url(r'^(?P<pk>[0-9]+)$', edit_leaderapplication, name='leaderapplication'),
    url(r'^apply/$', create_leaderapplication, name='create_leaderapplication'),
    
)

