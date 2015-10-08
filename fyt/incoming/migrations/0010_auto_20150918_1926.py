# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0009_auto_20150918_1253'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='incomingstudent',
            options={'ordering': ['name']},
        ),
    ]
