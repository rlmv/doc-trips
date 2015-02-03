

import requests


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

def lookup_email(net_id):
    """ 
    Lookup the email address of a user, given their NetId.
    """

    params = {'lookup': net_id, 'fields': ['email', 'netid']}
    r = requests.get('http://dndprofiles.dartmouth.edu/profile', params=params)

    # netid not found: {}
    if not r.json(): 
        raise EmailLookupException('NetId lookup failed: %s not found' % net_id)
    
    # mismatch, somehow...
    if r.json()['netid'] != net_id:
        raise EmailLookupException('NetId mismatch: %s != %s' % (r.json()['netid'], 
                                                                 net_id))

    return r.json()['email']
    
    
                     
