# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0015_auto_20150224_2104'),
        ('applications', '0029_auto_20150227_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadersupplement',
            name='assigned_trip',
            field=models.ForeignKey(null=True, blank=True, related_name='leaders', on_delete=django.db.models.deletion.SET_NULL, to='trips.ScheduledTrip'),
            preserve_default=True,
        ),
    ]
