# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def remove_permissions(apps, schema_editor):

    SitePermission = apps.get_model('permissions', 'SitePermission')
    for perm in SitePermission.objects.all():
        print("Deleting permission %s" % perm)
        perm.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0003_delete_sitepermissionstub'),
    ]

    operations = [
        migrations.RunPython(remove_permissions)
    ]
