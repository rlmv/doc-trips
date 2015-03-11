# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('trippees', '0005_auto_20150311_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='trippee',
            name='trips_year',
            field=models.ForeignKey(default=2015, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trippeeinfo',
            name='trips_year',
            field=models.ForeignKey(default=2015, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trippeeregistration',
            name='trips_year',
            field=models.ForeignKey(default=2015, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=False,
        ),
    ]
