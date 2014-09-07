
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

def get_or_create_user_by_netid(net_id, name=None):
    """ 
    Return the user with net_id. 

    Create the user if necesarry. If created, adds the optional name
    to the object as first_name. Does not search via name, since 
    names from different sources (CAS, DartDm lookup) can be slightly 
    different.
    """

    user, created = get_user_model().objects.get_or_create(username=net_id)

    if created:
        logger.info("creating user %r, %r" % (net_id, name))
        user.email = net_id + '@dartmouth.edu'
        if name:
            user.first_name = name
        user.save()

    return (user, created)
        
