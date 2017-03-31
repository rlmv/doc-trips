
import logging

import requests


logger = logging.getLogger(__name__)

# URL constants
DARTDM_URL = 'http://dartdm.dartmouth.edu/NetIdLookup/Lookup'
DNDPROFILES_URL = 'http://dndprofiles.dartmouth.edu/profile'

# Key constants
NETID = 'netid'
NAME_WITH_YEAR = 'name_with_year'
NAME_WITH_AFFIL = 'name_with_affil'


class DartDmLookupException(Exception):
    pass


def dartdm_lookup(query_string):
    """
    Search in the Dartmouth Directory Manager for a user.

    Return a list of user records.
    """
    # Single character query is not allowed
    if len(query_string) < 2:
        return []

    params = {'term': query_string}
    r = requests.get(DARTDM_URL, params=params)

    if isinstance(r.json(), dict):
        raise DartDmLookupException(r.json())

    return [{
        NETID: data['id'],
        NAME_WITH_YEAR: data['value'],
        NAME_WITH_AFFIL: data['label'],
    } for data in r.json()]


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
        logger.info(msg)
        raise EmailLookupException(msg)

    assert r.json()['netid'] == netid

    return r.json()['email']
