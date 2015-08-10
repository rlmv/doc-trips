# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('safety', '0005_incidentupdate_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incident',
            name='role',
            field=models.CharField(choices=[('TRIP_LEADER', 'Trip Leader'), ('CROO_MEMBER', 'Croo Member'), ('TRIPPEE', 'Trippee'), ('OTHER', 'Other')], verbose_name='What is your role on Trips?', max_length=20),
        ),
        migrations.AlterField(
            model_name='incidentupdate',
            name='role',
            field=models.CharField(choices=[('TRIP_LEADER', 'Trip Leader'), ('CROO_MEMBER', 'Croo Member'), ('TRIPPEE', 'Trippee'), ('OTHER', 'Other')], verbose_name='What is your role on Trips?', max_length=20),
        ),
    ]
