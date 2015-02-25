# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0004_route_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='stop',
            name='cost',
            field=models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stop',
            name='directions',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stop',
            name='distance',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stop',
            name='dropoff_time',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stop',
            name='pickup_time',
            field=models.TimeField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
