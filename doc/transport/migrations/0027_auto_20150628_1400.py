# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0026_auto_20150624_1624'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='externalbus',
            unique_together=set([('trips_year', 'route', 'section')]),
        ),
        migrations.AlterUniqueTogether(
            name='scheduledtransport',
            unique_together=set([('trips_year', 'route', 'date')]),
        ),
    ]
