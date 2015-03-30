# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trippees', '0002_auto_20150305_1852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trippee',
            name='trip_assignment',
            field=models.ForeignKey(to='trips.ScheduledTrip', on_delete=django.db.models.deletion.PROTECT, related_name='trippees'),
        ),
    ]
