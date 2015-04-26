# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0023_auto_20150325_1427'),
        ('trips', '0022_auto_20150422_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledtrip',
            name='dropoff_route',
            field=models.ForeignKey(blank=True, null=True, to='transport.Route', related_name='overridden_dropped_off_trips', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='scheduledtrip',
            name='pickup_route',
            field=models.ForeignKey(blank=True, null=True, to='transport.Route', related_name='overridden_picked_up_trips', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='scheduledtrip',
            name='return_route',
            field=models.ForeignKey(blank=True, null=True, to='transport.Route', related_name='overriden_returning_trips', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
    ]
