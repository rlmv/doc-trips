# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0030_leadersupplement_assigned_trip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leadersupplement',
            name='assigned_trip',
            field=models.ForeignKey(blank=True, null=True, to='trips.ScheduledTrip', on_delete=django.db.models.deletion.PROTECT, related_name='leaders'),
        ),
    ]
