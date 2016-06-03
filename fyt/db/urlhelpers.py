
from django.core.urlresolvers import reverse

"""
Collection of constants and utility functions used to automatically
generate and reverse urls for the database.
"""

DB_REGEX = {
    'LIST': r'^$',
    'CREATE': r'^create$',
    'DETAIL': r'^(?P<pk>[0-9]+)/$',
    'DELETE': r'^(?P<pk>[0-9]+)/delete$',
    'UPDATE': r'^(?P<pk>[0-9]+)/update$',
}


"""
Url names for db objects use the following pattern:
[lowercasemodelname]_[suffix], where suffix is one of
'list', 'create', 'update', 'delete', 'detail'.
"""


def reverse_index_url(db_object):
    """ Reverse the url to an Index (ListView).

    This may be problematic because it extracts trips_year from
    an object instance.
    TODO: change this to accept trips_year as an argument?
    """

    name = db_object.get_model_name_lower()
    urlpattern = '{}:{}_{}'.format('db', name, 'index')
    kwargs = {'trips_year': db_object.trips_year_id}

    return reverse(urlpattern, kwargs=kwargs)


def reverse_create_url(db_cls, trips_year):

    name = db_cls.get_model_name_lower()
    urlpattern = '{}:{}_{}'.format('db', name, 'create')
    kwargs = {'trips_year': trips_year.pk}

    return reverse(urlpattern, kwargs=kwargs)
