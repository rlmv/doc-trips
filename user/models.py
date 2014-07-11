from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

User = get_user_model()

class UserProfile(models.Model):
    """ Profile to  extend the User class. 

    We need to save the netid of every User, which cannot be
    done on the User model itself.
    """
    user = models.OneToOneField(User, unique=True)
    netid = models.CharField(max_length=40)


def create_profile(sender, instance, created, **kwargs):
    """ Create a UserProfile for every created User. """
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
post_save.connect(create_profile, sender=User) # register
