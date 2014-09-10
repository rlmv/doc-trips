# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0007_auto_20140830_2328'),
        ('leader', '0008_auto_20140910_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderapplication',
            name='available_triptypes',
            field=models.ManyToManyField(to='trip.TripType', blank=True, related_name='available_triptypes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='preferred_triptypes',
            field=models.ManyToManyField(to='trip.TripType', blank=True, related_name='preferred_leaders'),
            preserve_default=True,
        ),
    ]
