# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0032_auto_20150728_1315'),
        ('transport', '0036_auto_20150727_1826'),
    ]

    operations = [
        migrations.AddField(
            model_name='stoporder',
            name='stop_type',
            field=models.CharField(choices=[('PICKUP', 'PICKUP'), ('DROPOFF', 'DROPOFF')], default='DROPOFF', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stoporder',
            name='trip',
            field=models.ForeignKey(default=0, to='trips.Trip'),
            preserve_default=False,
        ),
    ]
