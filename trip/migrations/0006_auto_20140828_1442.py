# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0005_auto_20140728_1923'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scheduledtrip',
            options={'verbose_name': 'trip'},
        ),
        migrations.AlterModelOptions(
            name='triptemplate',
            options={'verbose_name': 'template'},
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='campsite_1',
            field=models.ForeignKey(related_name='trip_night_1', to='trip.Campsite'),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='campsite_2',
            field=models.ForeignKey(related_name='trip_night_2', to='trip.Campsite'),
        ),
    ]
