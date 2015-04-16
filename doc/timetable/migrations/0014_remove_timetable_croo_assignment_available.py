# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0013_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timetable',
            name='croo_assignment_available',
        ),
    ]
