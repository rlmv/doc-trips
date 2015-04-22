# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0021_auto_20150421_1503'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scheduledtrip',
            options={'ordering': ('section__name', 'template__name')},
        ),
    ]
