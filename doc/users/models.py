import logging

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import BaseUserManager, PermissionsMixin

from dartdm.lookup import lookup_email

logger = logging.getLogger(__name__)


class DartmouthUserManager(BaseUserManager):

    def get_by_netid(self, netid, name):
        """ 
        Return the user with netid. 

        Create the user if necesarry. If created, adds the optional name
        to the object as first_name. Does not search via name, since 
        names from different sources (CAS, DartDm lookup) can be slightly 
        different.
        """

        try:
            user = self.get(netid=netid)
            created = False
        except self.model.DoesNotExist:
            user = self.create_user(netid, name=name)
            created = True
                
        return (user, created)

    def create_user(self, netid, name, email=None):

        if email is None:
            email = lookup_email(netid)
        
        logger.info("Creating user %r, %r, %r" % (name, email, netid))
        user = self.create(netid=netid, email=email, name=name)

        return user
        
    def create_superuser(self, **kwargs):
        
        msg = ("create_superuser not implemented. "
               "Use 'manage.py setsuperuser' instead.")
        raise Exception(msg)


class DartmouthUser(PermissionsMixin):

    objects = DartmouthUserManager()

    netid = models.CharField(max_length=40, unique=True)
    email = models.EmailField('email address')
    email2 = models.EmailField('auxiliary email address', null=True, blank=True)
    name = models.CharField(max_length=255)

    last_login = models.DateTimeField('last login', blank=True, null=True)

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
        return '{} ({})'.format(self.name, self.netid)
        

