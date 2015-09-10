# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0014_remove_timetable_croo_assignment_available'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timetable',
            name='migration_date',
        ),
    ]
