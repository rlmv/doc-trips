from django.db import models
from django.conf import settings
from django.db.models.signals import post_save

class UserProfile(models.Model):
    """ Profile to  extend the User class. 

    We need to save the netid of every User, which cannot be
    done on the User model itself.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True)
    netid = models.CharField(max_length=40)
    did = models.CharField(max_length=40)
    uid = models.CharField(max_length=40)
    affil = models.CharField(max_length=40)
    alumni_id = models.CharField(max_length=40)
    auth_type = models.CharField(max_length=40)


def create_profile(sender, instance, created, **kwargs):
    """ Create a UserProfile for every created User. """
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
post_save.connect(create_profile, sender=settings.AUTH_USER_MODEL) # register
