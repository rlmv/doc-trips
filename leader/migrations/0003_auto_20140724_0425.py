# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0002_auto_20140723_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaderapplication',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False),
        ),
        migrations.AlterField(
            model_name='leadergrade',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False),
        ),
    ]
