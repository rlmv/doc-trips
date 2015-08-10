# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raids', '0006_init_raid_info'),
    ]

    operations = [
        migrations.RenameField(
            model_name='raidinfo',
            old_name='info',
            new_name='instructions',
        ),
    ]
