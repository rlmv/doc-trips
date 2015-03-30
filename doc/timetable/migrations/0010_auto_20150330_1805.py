# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0009_auto_20150319_2311'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timetable',
            name='trippee_assignment_posted',
        ),
        migrations.AddField(
            model_name='timetable',
            name='trippee_assignment_available',
            field=models.BooleanField(help_text='Turn this on to let Incoming Students see their trip assignments', default=False),
            preserve_default=True,
        ),
    ]
