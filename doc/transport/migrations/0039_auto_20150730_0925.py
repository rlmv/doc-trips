# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0038_auto_20150730_0922'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stoporder',
            unique_together=set([('trips_year', 'bus', 'trip')]),
        ),
    ]
