

from django.conf.urls import patterns, url, include

from trip.urls import * # TODO
from leader.urls import *

database_urlpatterns = patterns('', 
    url(r'^trips/', include(trip_urlpatterns)),
    url(r'^templates/', include(template_urlpatterns)),
    url(r'^types/', include(triptype_urlpatterns)),
    url(r'^campsites/', include(campsite_urlpatterns)),
    url(r'^sections/', include(section_urlpatterns)),
    url(r'^leaders/', include(leaderapplication_urlpatterns)),
)

urlpatterns = patterns('',
    # capture the 'trips_year' parameter which is passed to all db views                 
    url(r'^(?P<trips_year>[0-9]+)/', include(database_urlpatterns)),
)                       
                                  
   
def _reverse_db_url(db_object, urlpattern_suffix):
    """ Reverse a url for a database object instance. """ 
    
    name = db_object.get_reference_name()
    urlpattern = '{}:{}_{}'.format('db', name, urlpattern_suffix)
    kwargs = {'trips_year': db_object.trips_year_id,
              'pk': db_object.pk}
              
    return reverse(urlpattern, kwargs=kwargs)
        

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

    name = db_object.get_reference_name()
    urlpattern = '{}:{}_{}'.format('db', name, 'index')
    kwargs = {'trips_year': db_object.trips_year_id}
              
    return reverse(urlpattern, kwargs=kwargs)


