# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0004_auto_20150217_0642'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timetable',
            old_name='trippee_registration_closed',
            new_name='trippee_registrations_close',
        ),
        migrations.RenameField(
            model_name='timetable',
            old_name='trippee_registration_open',
            new_name='trippee_registrations_open',
        ),
    ]
