# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0003_auto_20150812_1744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='bus_assignment',
            field=models.ForeignKey(verbose_name='bus assignment (round-trip)', on_delete=django.db.models.deletion.PROTECT, null=True, related_name='riders_round_trip', to='transport.Stop', blank=True),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='bus_assignment_from_hanover',
            field=models.ForeignKey(verbose_name='bus assignment FROM Hanover (one-way)', on_delete=django.db.models.deletion.PROTECT, null=True, related_name='riders_from_hanover', to='transport.Stop', blank=True),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='bus_assignment_to_hanover',
            field=models.ForeignKey(verbose_name='bus assignment TO Hanover (one-way)', on_delete=django.db.models.deletion.PROTECT, null=True, related_name='riders_to_hanover', to='transport.Stop', blank=True),
        ),
    ]
