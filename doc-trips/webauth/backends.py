"""CAS authentication backend"""

from urllib.parse import urljoin
from xml.etree import ElementTree

import requests
from django.conf import settings
from django.contrib.auth import get_user_model

UserModel = get_user_model()


def parse_cas_success(tree):
    """ 
    Callback function for parsing Dartmouth's CAS response.
    
    Return the verified user. 
    """

    def findtext(text):
        tag_prefix = "{http://www.yale.edu/tp/cas}"
        return tree[0].findtext(tag_prefix + text)

    name = findtext('name')
    netid = findtext('netid')
    user, created = UserModel.objects.get_by_netid(netid, name)

    return user


def verify(ticket, service):
    """
    Verifies CAS 2.0+ XML-based authentication ticket.

    Returns user on success and None on failure.
    """

    params = {'ticket': ticket, 'service': service}

    # TODO: ensure that url uses https
    url = urljoin(settings.CAS_SERVER_URL, 'serviceValidate')
    r = requests.get(url, params=params)

    print(r.text)
    try:
        tree = ElementTree.fromstring(r.text)
        
        if tree[0].tag.endswith('authenticationSuccess'):
            #if settings.CAS_RESPONSE_CALLBACKS:
            #    cas_response_callbacks(tree)
            return parse_cas_success(tree)
        else:
            return None
    except Exception as e:
        # TODO: pass this? return None?
        raise 


class WebAuthBackend():
    """ CAS authentication backend """

    supports_object_permissions = False
    supports_inactive_user = False

    def authenticate(self, ticket, service):
        """
        Verifies CAS ticket and gets or creates User object.
        """
        return verify(ticket, service)

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""

        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
