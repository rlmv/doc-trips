# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0029_auto_20150721_1452')
    ]
    operations = [
        migrations.RenameModel(
            old_name='ScheduledTrip',
            new_name='Trip'
        ),
    ]
