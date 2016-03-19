

import requests
import logging

logger = logging.getLogger(__name__)


DARTDM_URL = 'http://dartdm.dartmouth.edu/NetIdLookup/Lookup'
DNDPROFILES_URL = 'http://dndprofiles.dartmouth.edu/profile'


def dartdm_lookup(query_string):
    """
    Search in the DartDm for a user.

    TODO: catch requests library errors
    """
    params = {'term': query_string}
    r = requests.get(DARTDM_URL, params=params)
    return r.json()


class EmailLookupException(Exception):
    pass


def lookup_email(netid):
    """
    Lookup the email address of a user, given their NetId.
    """
    params = {'lookup': netid, 'fields': ['email', 'netid']}
    r = requests.get(DNDPROFILES_URL, params=params)

    # netid not found
    if not r.json():
        msg = 'Email lookup failed: NetId %s not found' % netid
        logger.error(msg)
        raise EmailLookupException(msg)

    assert r.json()['netid'] == netid

    return r.json()['email']
