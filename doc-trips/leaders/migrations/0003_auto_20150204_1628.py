# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leaders', '0002_auto_20150126_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaderapplication',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='leadergrade',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
