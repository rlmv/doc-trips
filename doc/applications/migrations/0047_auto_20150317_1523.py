# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0046_auto_20150311_1408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crooapplicationgrade',
            name='scratchpad',
        ),
        migrations.RemoveField(
            model_name='leaderapplicationgrade',
            name='scratchpad',
        ),
    ]
