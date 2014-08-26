
from django.conf.urls import patterns, url

""" Test urls for test_get_absolute_url """
urlpatterns = patterns('', 
    url(r'^(?P<trips_year>[0-9]+)/(?P<pk>[0-9]+)$', lambda r: None, name='test_url')
)
