from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class SitePermissionManager(models.Manager):
    """ Manager class for SitePermission model. """

    def get_query_set(self):
        qs = super(SitePermissionManager, self).get_query_set()
        return qs.filter(content_type__name='site_permission')


class SitePermission(Permission):
    """ Implements global permission, not attached to a model.

    Shamelessly lifted from http://stackoverflow.com/a/13952198/3818777
    """

    objects = SitePermissionManager()

    class Meta:
        proxy = True # proxy models are cool!

    def save(self, *args, **kwargs):
        ct, created = ContentType.objects.get_or_create(
            name="site_permission", app_label=self._meta.app_label
        )
        self.content_type = ct
        super(SitePermission, self).save(*args, **kwargs)

