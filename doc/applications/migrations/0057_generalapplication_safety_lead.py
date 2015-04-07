# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0056_auto_20150407_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalapplication',
            name='safety_lead',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
