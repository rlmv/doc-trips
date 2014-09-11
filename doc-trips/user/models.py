import logging

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save

from django.contrib.auth.models import AbstractUser, UserManager

logger = logging.getLogger(__name__)

class DartmouthUserManager(UserManager):

    def get_by_netid(self, net_id, name=None):
        """ 
        Return the user with net_id. 

        Create the user if necesarry. If created, adds the optional name
        to the object as first_name. Does not search via name, since 
        names from different sources (CAS, DartDm lookup) can be slightly 
        different.
        """

        user, created = self.get_or_create(net_id=net_id)

        if created:
            logger.info("creating user %r, %r" % (name, net_id))
            user.email = net_id + '@dartmouth.edu'
            if name:
                user.first_name = name
                user.save()
                
        return (user, created)
    

class DartmouthUserModel(AbstractUser):

    objects = DartmouthUserManager()
    net_id = models.CharField(max_length=40, unique=True)

    USERNAME_FIELD = 'net_id'

    def __str__(self):
        return '{} ({})'.format(self.get_short_name(), self.net_id)
        

