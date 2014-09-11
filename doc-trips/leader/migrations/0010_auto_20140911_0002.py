# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0009_auto_20140910_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaderapplication',
            name='available_triptypes',
            field=models.ManyToManyField(related_name='available_triptypes', verbose_name='Available types of trips', to='trip.TripType', blank=True),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='preferred_triptypes',
            field=models.ManyToManyField(related_name='preferred_leaders', verbose_name='Preferred types of trips', to='trip.TripType', blank=True),
        ),
    ]
