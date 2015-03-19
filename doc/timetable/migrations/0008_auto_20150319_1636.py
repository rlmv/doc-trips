# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0007_auto_20150319_1634'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timetable',
            name='croo_assignment_posted',
        ),
        migrations.RemoveField(
            model_name='timetable',
            name='leader_assignment_posted',
        ),
        migrations.AddField(
            model_name='timetable',
            name='croo_assignment_available',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='timetable',
            name='leader_assignment_available',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
