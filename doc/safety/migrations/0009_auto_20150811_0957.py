# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('safety', '0008_auto_20150810_1333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incident',
            name='user_role',
        ),
        migrations.RemoveField(
            model_name='incidentupdate',
            name='user_role',
        ),
    ]
