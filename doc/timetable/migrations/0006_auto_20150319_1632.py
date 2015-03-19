# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0005_auto_20150311_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetable',
            name='application_status_posted',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='timetable',
            name='croo_assignment_posted',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
    ]
