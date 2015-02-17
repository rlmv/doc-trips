# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0003_auto_20150217_0639'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timetable',
            old_name='applications_closed',
            new_name='applications_close',
        ),
    ]
