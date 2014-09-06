

import requests

def dartdm_lookup(query_string):
    """ 

    TODO: catch requests library errors
    """
    payload = {'term': query_string}
    r = requests.get('http://dartdm.dartmouth.edu/NetIdLookup/Lookup', 
                     params=payload)
    return r.json()
