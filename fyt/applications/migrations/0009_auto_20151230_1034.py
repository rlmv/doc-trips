# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0008_auto_20151230_1022'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='GeneralApplication',
            name='hanover_in_fall'
        ),
        migrations.RenameField(
            model_name='GeneralApplication',
            old_name='_hanover_in_fall',
            new_name='hanover_in_fall'
        )
    ]
