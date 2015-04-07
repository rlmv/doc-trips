# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0010_auto_20150330_1805'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetable',
            name='hide_volunteer_page',
            field=models.BooleanField(default=False, help_text="Enabling this will hide the database Volunteers page from everyone except directors. Use this during grading to prevent graders from seeing applicant's scores."),
            preserve_default=True,
        ),
    ]
