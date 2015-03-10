# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0042_auto_20150310_1046'),
    ]

    operations = [
        migrations.RenameField(
            model_name='crooapplicationgrade',
            old_name='qualification',
            new_name='qualifications',
        ),
    ]
