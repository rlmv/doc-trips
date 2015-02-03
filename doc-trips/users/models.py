import logging

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import BaseUserManager, PermissionsMixin

from dartdm.lookup import lookup_email

logger = logging.getLogger(__name__)


class DartmouthUserManager(BaseUserManager):

    def get_by_netid(self, net_id, name):
        """ 
        Return the user with net_id. 

        Create the user if necesarry. If created, adds the optional name
        to the object as first_name. Does not search via name, since 
        names from different sources (CAS, DartDm lookup) can be slightly 
        different.
        """

        try:
            user = self.get(net_id=net_id)
            created = False
        except self.model.DoesNotExist:
            logger.info("creating user %r, %r" % (name, net_id))
            user = self.create_user(net_id, name=name)
            created = True
                
        return (user, created)

    def create_user(self, net_id, name, email=None):

        email = lookup_email(net_id)
        user = self.create(net_id=net_id, email=email, name=name)

        return user
        
    def create_superuser(self, **kwargs):
        
        msg = ("create_superuser not implemented. "
               "Use 'manage.py setsuperuser' instead.")
        raise Exception(msg)


class DartmouthUser(PermissionsMixin):

    objects = DartmouthUserManager()

    net_id = models.CharField(max_length=40, unique=True)
    email = models.EmailField('email address')
    name = models.CharField(max_length=255)

    last_login = models.DateTimeField('last login', blank=True, null=True)

    # used by Django Admin
    @property 
    def is_active(self):
        return True 
    @property
    def is_staff(self):
        return self.is_superuser

    USERNAME_FIELD = 'net_id'
    REQUIRED_FIELDS = ['email', 'name']

    def get_short_name(self):
        return self.name

    def get_full_name(self):
        return self.name

    def get_username(self):
        return self.net_id

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False
    
    def __str__(self):
        return '{} ({})'.format(self.name, self.net_id)
        

