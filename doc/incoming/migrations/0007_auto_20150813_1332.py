# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0006_auto_20150813_1310'),
    ]

    operations = [
        migrations.RenameField(
            model_name='incomingstudent',
            old_name='bus_assignment',
            new_name='bus_assignment_round_trip',
        ),
    ]
