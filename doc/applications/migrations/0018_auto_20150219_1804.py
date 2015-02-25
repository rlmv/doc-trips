# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0017_auto_20150219_1803'),
    ]

    operations = [
        migrations.RenameField(
            model_name='generalapplication',
            old_name='assignment_preference',
            new_name='role_preference',
        ),
    ]
