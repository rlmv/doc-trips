# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0008_auto_20150319_1636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timetable',
            name='application_status_available',
            field=models.BooleanField(default=False, help_text='Turn this on once all decisions have been made regarding Leaders and Croos'),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='croo_assignment_available',
            field=models.BooleanField(default=False, help_text='Turn this on to let Croo members see their assigned Croo'),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='leader_assignment_available',
            field=models.BooleanField(default=False, help_text='Turn this on to let Trip Leaders see information about their assigned trip'),
        ),
    ]
