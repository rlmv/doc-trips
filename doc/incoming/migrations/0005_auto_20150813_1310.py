# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0044_auto_20150812_1940'),
        ('incoming', '0004_auto_20150812_1905'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registration',
            old_name='bus_stop',
            new_name='bus_stop_round_trip',
        ),
        migrations.AddField(
            model_name='registration',
            name='bus_stop_from_hanover',
            field=models.ForeignKey(to='transport.Stop', on_delete=django.db.models.deletion.PROTECT, related_name='requests_from_hanover', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='bus_stop_to_hanover',
            field=models.ForeignKey(to='transport.Stop', on_delete=django.db.models.deletion.PROTECT, related_name='requests_to_hanover', null=True, blank=True),
            preserve_default=True,
        ),
    ]
