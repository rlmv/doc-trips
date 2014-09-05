# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20140902_0102'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SitePermission',
        ),
    ]
