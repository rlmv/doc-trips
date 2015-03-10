# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0016_auto_20150310_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptemplate',
            name='campsite1',
            field=models.ForeignKey(verbose_name='campsite 1', related_name='trip_night_1', on_delete=django.db.models.deletion.PROTECT, to='trips.Campsite'),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='campsite2',
            field=models.ForeignKey(verbose_name='campsite 2', related_name='trip_night_2', on_delete=django.db.models.deletion.PROTECT, to='trips.Campsite'),
        ),
    ]
