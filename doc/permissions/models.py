from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

""" 
Implements permissions not attached to a model.

Shamelessly adapted from http://stackoverflow.com/a/13952198/3818777

Permissions are set on the SitePermission model.
This lets us do SitePermission.objects.create(codename, name)
"""

def get_content_type():
    """ Return the SitePermission content type """
    return ContentType.objects.get_for_model(
        SitePermission, for_concrete_model=False
    )


class SitePermissionManager(models.Manager):
    """ Manager class for SitePermission model. """

    def get_queryset(self):
        qs = super(SitePermissionManager, self).get_queryset()
        return qs.filter(content_type=get_content_type())


class SitePermission(Permission):
    """ Proxy model for the django Permissions model. """
    objects = SitePermissionManager()

    class Meta:
        proxy = True # proxy models are cool!

    def save(self, *args, **kwargs):
        self.content_type = get_content_type()
        super(SitePermission, self).save(*args, **kwargs)

