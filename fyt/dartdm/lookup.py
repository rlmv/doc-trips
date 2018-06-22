import logging
from json import JSONDecodeError

import requests


log = logging.getLogger(__name__)

# URL constants. These endpoints have changed in the past,
# so check the source of https://lookup.dartmouth.edu/ if
# the lookup is broken.
#
# The following are valid query parameters:
# q=Lucia
# includeAlum=true
# field=uid
# field=displayName
# field=eduPersonPrimaryAffiliation
# field=mail&field=eduPersonNickname
# field=dcDeptclass
# field=dcAffiliation
# field=telephoneNumber
# field=dcHinmanaddr
DARTDM_URL = 'https://api-lookup.dartmouth.edu/v1/lookup'
DNDPROFILES_URL = 'http://dndprofiles.dartmouth.edu/profile'

# Key constants
NETID = 'netid'
NAME = 'name'


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

    r = requests.get(DARTDM_URL, params={'q': query_string})

    if 'error' in r.json():
        log.info(r.json())
        return []

    return [{
        NETID: data['uid'],
        NAME: data['displayName'],
    } for data in r.json()['users']]


class EmailLookupException(Exception):
    pass


def lookup_email(netid):
    """
    Lookup the email address of a user, given their NetId.
    """
    params = {'lookup': netid, 'fields': ['email', 'netid']}

    try:
        r = requests.get(DNDPROFILES_URL, params=params)
    except requests.RequestException as e:
        log.error(e)
        raise EmailLookupException from e

    try:
        r_json = r.json()
    except JSONDecodeError as e:
        log.error(e)
        raise EmailLookupException from e

    # Not found
    if not r_json:
        msg = 'Email lookup failed: NetId %s not found' % netid
        log.error(msg)
        raise EmailLookupException(msg)

    assert r_json['netid'] == netid

    return r_json['email']
