

from django.conf.urls import patterns, url, include

DB_REGEX = {
    'LIST': r'^$',
    'CREATE': r'^create$', 
    'DETAIL': r'^(?P<pk>[0-9]+)/$',
    'DELETE': r'^(?P<pk>[0-9]+)/delete$',
    'UPDATE': r'^(?P<pk>[0-9]+)/update$',
}

"""DB_MODEL_NAME_MAPPING = {
    ScheduledTrip: 'scheduledtrip', 
    TripTemplate: 'triptemplate', 
    TripType: 'triptype',
    Section: 'section',
    Campsite: 'campsite',
}"""

def model_reference_name(model):
    return DB_MODEL_NAME_MAPPING[model]

from trip.urls import (trip_urlpatterns, template_urlpatterns, triptype_urlpatterns, 
                       campsite_urlpatterns, section_urlpatterns)
from leader.urls import *
from db.views import DatabaseIndexView

database_urlpatterns = patterns('', 
    url(r'^$', DatabaseIndexView.as_view(), name='db_index'),
    url(r'^trips/', include(trip_urlpatterns)),
    url(r'^templates/', include(template_urlpatterns)),
    url(r'^types/', include(triptype_urlpatterns)),
    url(r'^campsites/', include(campsite_urlpatterns)),
    url(r'^sections/', include(section_urlpatterns)),
    url(r'^leaders/', include(leaderapplication_urlpatterns)),
)

urlpatterns = patterns('',
    url(r'^$', RedirectToCurrentDatabase.as_view(), name='db_redirect'),
    # capture the 'trips_year' parameter which is passed to all db views           
    url(r'^(?P<trips_year>[0-9]+)/', include(database_urlpatterns)),
)

"""
Url names for db objects use the following pattern:
[lowercasemodelname]_[suffix], where suffix is one of 
'list', 'create', 'update', 'delete', 'detail'.
"""

def _reverse_db_url(db_object, urlpattern_suffix):
    """ Reverse a url for a database object instance. """ 
    
    name = db_object.get_model_name()
    urlpattern = '{}:{}_{}'.format('db', name, urlpattern_suffix)
    kwargs = {'trips_year': db_object.trips_year_id,
              'pk': db_object.pk}
              
    return reverse(urlpattern, kwargs=kwargs)

def get_detail_url(db_object):
    return _reverse_db_url(db_object, 'detail')

def get_delete_url(db_object):
    """ Reverse the url to delete db_object. """
    return _reverse_db_url(db_object, 'delete')


def get_update_url(db_object):
    """ Reverse the url to update db_object. """
    return _reverse_db_url(db_object, 'update')


def get_index_url(db_object):
    """ Reverse the url to an Index (ListView). 

    This may be problematic because it extracts trips_year from 
    an object instance. 
    TODO: change this to accept trips_year as an argument?
    """

    name = db_object.get_model_name()
    urlpattern = '{}:{}_{}'.format('db', name, 'index')
    kwargs = {'trips_year': db_object.trips_year_id}
              
    return reverse(urlpattern, kwargs=kwargs)


def get_create_url(db_cls, trips_year):

    name = db_cls.get_model_name()
    urlpattern = '{}:{}_{}'.format('db', name, 'create')
    kwargs = {'trips_year': trips_year.pk}
    
    return reverse(urlpattern, kwargs=kwargs)
    
