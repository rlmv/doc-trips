# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0021_auto_20140918_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaderapplication',
            name='assigned_trip',
            field=models.ForeignKey(to='trip.ScheduledTrip', null=True, blank=True, related_name='leaders', on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
