# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0044_auto_20150310_1104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crooapplicationgrade',
            name='potential_croos',
        ),
    ]
