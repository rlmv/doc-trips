from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType



class SitePermissionStub(models.Model):

    pass


class SitePermissionManager(models.Manager):
    """ Manager class for SitePermission model. """

    def get_queryset(self):
        qs = super(SitePermissionManager, self).get_queryset()
        content_type = ContentType.objects.get_for_model(SitePermissionStub)
        return qs.filter(content_type=content_type)


class SitePermission(Permission):
    """ Implements global permission, not attached to a model.

    Shamelessly lifted from http://stackoverflow.com/a/13952198/3818777
    """

    objects = SitePermissionManager()

    class Meta:
        proxy = True # proxy models are cool!

    def save(self, *args, **kwargs):
        self.content_type = ContentType.objects.get_for_model(SitePermissionStub)
        super(SitePermission, self).save(*args, **kwargs)
    
    

