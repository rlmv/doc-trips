import logging

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import BaseUserManager, PermissionsMixin

from doc.dartdm.lookup import lookup_email

logger = logging.getLogger(__name__)

class DartmouthUserManager(BaseUserManager):

    def get_or_create_by_netid(self, netid, name, did=None):
        """ 
        Return the user with netid. 

        Create the user if necesarry. Does not search via name, since 
        names from different sources (CAS, DartDm lookup) can be slightly 
        different.

        Because we added the did field, some users do not have it set. 
        Also, users added via the permissions/access page don't have a
        did set. Check and fix it if possible. 
        """

        try:
            user = self.get(netid=netid)
            if user.did == '' and did is not None:
                user.did = did
                user.save()
                logger.info("Adding DID %s to existing user %s" % (did, user))
            created = False
        except self.model.DoesNotExist:
            user = self.create_user(netid, name=name, did=did)
            created = True
                
        return (user, created)

    def create_user(self, netid, name, email=None, did=None):

        if email is None:
            email = lookup_email(netid)

        if did is None:
            did = ''
        
        logger.info("Creating user %r, %r, %r, %r" % (name, email, netid, did))
        user = self.create(netid=netid, did=did, email=email, name=name)

        return user
        
    def create_superuser(self, **kwargs):
        
        msg = ("create_superuser not implemented. "
               "Use 'manage.py setsuperuser' instead.")
        raise Exception(msg)


class DartmouthUser(PermissionsMixin):

    objects = DartmouthUserManager()

    netid = models.CharField(max_length=20, unique=True)
    # DID (Dartmouth ID) is not guaranteed to be set
    did = models.CharField(max_length=20)
    email = models.EmailField('email address')
    email2 = models.EmailField('auxiliary email address', null=True, blank=True)
    name = models.CharField(max_length=255, db_index=True)

    last_login = models.DateTimeField('last login', blank=True, null=True)

    class Meta:
        ordering = ['name']

    # used by Django Admin
    @property 
    def is_active(self):
        return True 
    @property
    def is_staff(self):
        return self.is_superuser

    USERNAME_FIELD = 'netid'
    REQUIRED_FIELDS = ['email', 'name']

    def get_short_name(self):
        return self.name

    def get_full_name(self):
        return self.name

    def get_username(self):
        return self.netid

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False
    
    def __str__(self):
        #return '{} ({})'.format(self.name, self.netid)
        return str(self.name)
        

