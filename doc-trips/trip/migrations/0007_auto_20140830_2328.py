# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0006_auto_20140828_1442'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='scheduledtrip',
            unique_together=set([('template', 'section', 'trips_year')]),
        ),
    ]
