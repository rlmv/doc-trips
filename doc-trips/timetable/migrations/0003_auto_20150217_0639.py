# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0002_auto_20150206_1623'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timetable',
            old_name='leader_application_closed',
            new_name='applications_closed',
        ),
        migrations.RenameField(
            model_name='timetable',
            old_name='leader_application_open',
            new_name='applications_open',
        ),
        migrations.RemoveField(
            model_name='timetable',
            name='crooapplication_closed',
        ),
        migrations.RemoveField(
            model_name='timetable',
            name='crooapplication_open',
        ),
    ]
