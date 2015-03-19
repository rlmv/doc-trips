# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0006_auto_20150319_1632'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timetable',
            name='application_status_posted',
        ),
        migrations.AddField(
            model_name='timetable',
            name='application_status_available',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
