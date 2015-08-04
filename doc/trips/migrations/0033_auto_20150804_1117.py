# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0032_auto_20150728_1315'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='dropoff_time',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='trip',
            name='pickup_time',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
