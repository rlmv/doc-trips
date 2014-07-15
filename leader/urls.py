
from django.conf.urls import patterns, url

from .views import *

urlpatterns = patterns('', 
    url(r'^(?P<pk>[0-9]+)$', edit_leaderapplication, name='leaderapplication'),
    url(r'^$', create_leaderapplication, name='create_leaderapplication'),
    
)

