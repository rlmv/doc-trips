# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('safety', '0006_auto_20150810_1317'),
    ]

    operations = [
        migrations.RenameField(
            model_name='incident',
            old_name='role',
            new_name='user_role',
        ),
        migrations.RenameField(
            model_name='incidentupdate',
            old_name='role',
            new_name='user_role',
        ),
    ]
