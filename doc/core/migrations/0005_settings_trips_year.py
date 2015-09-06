# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('core', '0004_auto_20150527_0024'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='trips_year',
            field=models.ForeignKey(default=2015, editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=False,
        ),
    ]
