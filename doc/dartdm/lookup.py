

import requests
import logging

logger = logging.getLogger(__name__)


def dartdm_lookup(query_string):
    """ 
    Search in the DartDm for a user.
    
    TODO: catch requests library errors
    """
    payload = {'term': query_string}
    r = requests.get('http://dartdm.dartmouth.edu/NetIdLookup/Lookup', 
                     params=payload)
    return r.json()


class EmailLookupException(Exception):
    pass

def lookup_email(netid):
    """ 
    Lookup the email address of a user, given their NetId.
    """

    params = {'lookup': netid, 'fields': ['email', 'netid']}
    r = requests.get('http://dndprofiles.dartmouth.edu/profile', params=params)

    # netid not found: {}
    if not r.json(): 
        msg = 'Email lookup failed: NetId %s not found' % netid
        logger.error(msg, extra={'request': request})
        raise EmailLookupException(msg)
    
    # mismatch, somehow...
    if r.json()['netid'] != netid:
        raise EmailLookupException('Email lookup failed: NetId mismatch: %s != %s' % (r.json()['netid'], 
                                                                 netid))

    return r.json()['email']
    
    
                     
