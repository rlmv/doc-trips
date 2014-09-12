import logging

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save

from django.contrib.auth.models import AbstractUser, UserManager

logger = logging.getLogger(__name__)


class DartmouthUserManager(UserManager):

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
            email = net_id + '@dartmouth.edu'
            # sets 'unusable password':
            user = self.create_user(net_id, name=name, email=email)
            created = True
                
        return (user, created)

    def create_user(self, net_id_or_username, name=None, **kwargs):
        
        if not net_id_or_username:
            raise ValueError('DartmouthUser must have netid')

        password = kwargs.pop('password', None)
        if name is None:
            name = net_id_or_username

        user = self.model(net_id=net_id_or_username, 
                          username=net_id_or_username, 
                          name=name, **kwargs)

        user.set_password(password)
        user.save()
        return user
        
    def create_superuser(self, **kwargs):
        
        msg = ("create_superuser not implemented. "
               "Use 'manage.py setsuperuser' instead.")
        raise Exception(msg)


class DartmouthUser(AbstractUser):

    objects = DartmouthUserManager()
    net_id = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=255)

    USERNAME_FIELD = 'net_id'
    REQUIRED_FIELDS = ['name']
    
    def __str__(self):
        return '{} ({})'.format(self.name, self.net_id)
        

