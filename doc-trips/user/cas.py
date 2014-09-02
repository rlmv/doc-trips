
import logging

from django.contrib.auth import get_user_model
User = get_user_model()

logger = logging.getLogger(__name__)


def dartmouth_cas_callback(tree):
    """ Callback function for parsing Dartmouth's CAS response.
    
    This is called by the django_cas backend. 
    tree is a ElementTree object. 
    """

    tag_prefix = "{http://www.yale.edu/tp/cas}"
    findtext = lambda x: tree[0].findtext(tag_prefix + x)

    username = findtext('name')
    username = '_'.join(username.split())
    netid = findtext('netid')
    user_str = findtext('user') # fmt: username @DARTMOUTH.EDU

    email = netid + '@dartmouth.edu'
    
    # hack hack: CAS backend uses the tree[0][0] field
    # to get the user - we want to identify by username, 
    # not the user_str, so we substitute this in.
    tree[0][0].text = username

    logger.info("creating user %s" % username)
    user, created = User.objects.get_or_create(username=username, 
                                               email=email)
    if created:
        ## TODO: hacky - hack - the CAS package only allows admin 
        ## login for staff, fix it.
        user.is_staff = True
        # TODO: this gives all users admin priveleges, change this
        user.is_superuser = True; 
        
        profile = user.userprofile
        profile.netid = netid
        profile.did = findtext('did')
        profile.uid = findtext('uid')
        profile.affil = findtext('affil')
        profile.alumni_id = findtext('alumniid')
        profile.auth_type = findtext('authType')
        
        # profile.name = username
        user.save()
        profile.save()
