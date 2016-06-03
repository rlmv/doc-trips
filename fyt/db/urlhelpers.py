
"""
Constants for generating and reversing urls the database.
"""

DB_REGEX = {
    'LIST': r'^$',
    'CREATE': r'^create$',
    'DETAIL': r'^(?P<pk>[0-9]+)/$',
    'DELETE': r'^(?P<pk>[0-9]+)/delete$',
    'UPDATE': r'^(?P<pk>[0-9]+)/update$',
}
