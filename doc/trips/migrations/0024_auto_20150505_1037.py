# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0023_auto_20150426_0800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduledtrip',
            name='dropoff_route',
            field=models.ForeignKey(related_name='overridden_dropped_off_trips', blank=True, help_text='leave blank to use default route from template', null=True, on_delete=django.db.models.deletion.PROTECT, to='transport.Route'),
        ),
        migrations.AlterField(
            model_name='scheduledtrip',
            name='pickup_route',
            field=models.ForeignKey(related_name='overridden_picked_up_trips', blank=True, help_text='leave blank to use default route from template', null=True, on_delete=django.db.models.deletion.PROTECT, to='transport.Route'),
        ),
        migrations.AlterField(
            model_name='scheduledtrip',
            name='return_route',
            field=models.ForeignKey(related_name='overriden_returning_trips', blank=True, help_text='leave blank to use default route from template', null=True, on_delete=django.db.models.deletion.PROTECT, to='transport.Route'),
        ),
    ]
