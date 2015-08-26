# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('safety', '0009_auto_20150811_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incident',
            name='trip',
            field=models.ForeignKey(verbose_name='On what trip did this incident occur?', to='trips.Trip', blank=True, null=True),
        ),
    ]
