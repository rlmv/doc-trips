# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0033_auto_20150722_1649'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stoporder',
            unique_together=set([('trips_year', 'bus', 'stop')]),
        ),
    ]
