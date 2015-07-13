# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0046_auto_20150630_1428'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='incomingstudent',
            unique_together=set([('netid', 'trips_year')]),
        ),
    ]
