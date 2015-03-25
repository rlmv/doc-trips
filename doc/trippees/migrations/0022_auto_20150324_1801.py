# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0017_auto_20150310_1431'),
        ('trippees', '0021_auto_20150321_1353'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='available_sections',
            field=models.ManyToManyField(related_name='available_trippees', blank=True, to='trips.Section'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='available_triptypes',
            field=models.ManyToManyField(related_name='available_trippees', to='trips.TripType', blank=True, verbose_name='available types of trips'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='preferred_sections',
            field=models.ManyToManyField(related_name='prefering_trippees', blank=True, to='trips.Section'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='preferred_triptypes',
            field=models.ManyToManyField(related_name='preferring_trippees', to='trips.TripType', blank=True, verbose_name='preferred types of trips'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='unavailable_sections',
            field=models.ManyToManyField(related_name='unavailable_trippees', blank=True, to='trips.Section'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='unavailable_triptypes',
            field=models.ManyToManyField(related_name='unavailable_trippees', to='trips.TripType', blank=True, verbose_name='unavailable types of trips'),
            preserve_default=True,
        ),
    ]
