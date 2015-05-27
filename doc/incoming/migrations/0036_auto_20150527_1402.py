# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0035_auto_20150527_0034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='ethnic_code',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='gender',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='incoming_status',
            field=models.CharField(choices=[('EXCHANGE', 'Exchange'), ('TRANSFER', 'Transfer'), ('FIRSTYEAR', 'First Year')], blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='name',
            field=models.CharField(max_length=512),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='trip_assignment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='trippees', to='trips.ScheduledTrip'),
        ),
    ]
