from django.db import models
from django.conf import settings
from django.db.models.signals import post_save

from django.contrib.auth.models import AbstractUser, UserManager


class DartmouthUserModel(AbstractUser):

    objects = UserManager()
    net_id = models.CharField(max_length=40, unique=True)

    USERNAME_FIELD = 'net_id'

    def __str__(self):
        return '{} ({})'.format(self.get_short_name(), self.net_id)
        

