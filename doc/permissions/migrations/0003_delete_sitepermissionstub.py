# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0002_sitepermissionstub'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SitePermissionStub',
        ),
    ]
