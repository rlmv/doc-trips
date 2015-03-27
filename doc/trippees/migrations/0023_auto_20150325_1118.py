# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trippees', '0022_auto_20150324_1801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='unavailable_triptypes',
            field=models.ManyToManyField(verbose_name='unavailable trip types', blank=True, to='trips.TripType', related_name='unavailable_trippees'),
        ),
    ]
