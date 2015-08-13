# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0005_auto_20150813_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='bus_stop_round_trip',
            field=models.ForeignKey(related_name='requests_round_trip', blank=True, verbose_name='Where would you like to be bussed from/to?', null=True, on_delete=django.db.models.deletion.PROTECT, to='transport.Stop'),
        ),
    ]
