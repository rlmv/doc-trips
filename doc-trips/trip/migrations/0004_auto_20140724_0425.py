# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0003_auto_20140723_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campsite',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False),
        ),
        migrations.AlterField(
            model_name='scheduledtrip',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False),
        ),
        migrations.AlterField(
            model_name='section',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False),
        ),
        migrations.AlterField(
            model_name='triptype',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False),
        ),
    ]
