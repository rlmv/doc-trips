"""CAS authentication backend"""

from urllib.parse import urljoin
from xml.etree import ElementTree

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from user.models import DartmouthUserModel as User


__all__ = ['CASBackend']


def cas_response_callbacks(tree):
    """ 
    Process CAS response. 

    For each callback specified in CAS_RESPONSE_CALLBACKS, 
    run the callback with the response ElementTree.
    """

    callbacks = getattr(settings, 'CAS_RESPONSE_CALLBACKS', [])

    for path in callbacks:
        module, callback = path.rsplit('.', 1)
        mod = __import__(module, fromlist=[callback])
        func = getattr(mod, callback)
        func(tree)


def verify(ticket, service):
    """
    Verifies CAS 2.0+ XML-based authentication ticket.

    Returns username on success and None on failure.
    """

    params = {'ticket': ticket, 'service': service}

    # TODO: ensure that url uses https
    url = urljoin(settings.CAS_SERVER_URL, 'serviceValidate')
    r = requests.get(url, params=params)

    try:
        tree = ElementTree.fromstring(r.text)

        #Useful for debugging
        #from xml.dom.minidom import parseString
        #from xml.etree import ElementTree
        #txt = ElementTree.tostring(tree)
        #print parseString(txt).toprettyxml()
        
        if tree[0].tag.endswith('authenticationSuccess'):
            if settings.CAS_RESPONSE_CALLBACKS:
                cas_response_callbacks(tree)
            return tree[0][0].text
        else:
            return None
    except Exception as e:
        raise 


class CASBackend():
    """ CAS authentication backend """

    supports_object_permissions = False
    supports_inactive_user = False

    def authenticate(self, ticket, service):
        """
        Verifies CAS ticket and gets or creates User object.
        """

        username = verify(ticket, service)
        if not username:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        return user

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
