
import logging

from django.contrib.auth import get_user_model

from user import get_or_create_user_by_netid

logger = logging.getLogger(__name__)

""" 
Note: the we are using the Dartmouth NetId as the username, 
and setting first_name to the name of the person.
"""

def dartmouth_cas_callback(tree):
    """ Callback function for parsing Dartmouth's CAS response.
    
    This is called by the django_cas backend. 
    tree is a ElementTree object. 
    """

    def findtext(text):
        tag_prefix = "{http://www.yale.edu/tp/cas}"
        return tree[0].findtext(tag_prefix + text)

    name = findtext('name')
    netid = findtext('netid')
    user_str = findtext('user') # fmt: username @DARTMOUTH.EDU

    # added in the get_or_create_user_by_netid function
    # email = netid + '@dartmouth.edu'
    
    # hack hack: CAS backend uses the tree[0][0] field
    # to get the user - we want to identify use NetId as the username
    # because it is guaranteed unique
    tree[0][0].text = netid

    user, created = get_or_create_user_by_netid(netid, name)
    
    if created:
        ## TODO: hacky - hack - the CAS package only allows admin 
        ## login for staff, fix it.
        user.is_staff = True
        # TODO: this gives all users admin priveleges, change this
        user.is_superuser = True; 

        user.save()
