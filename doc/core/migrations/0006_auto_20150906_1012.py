# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_settings_trips_year'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='settings',
            unique_together=set([('trips_year',)]),
        ),
    ]
