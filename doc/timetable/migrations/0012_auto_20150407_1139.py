# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0011_timetable_hide_volunteer_page'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timetable',
            name='hide_volunteer_page',
            field=models.BooleanField(help_text="Enabling this will hide the database Volunteers page from everyone except directors and trip leader trainers. Use this during grading to prevent graders from seeing applicant's scores.", default=False),
        ),
    ]
