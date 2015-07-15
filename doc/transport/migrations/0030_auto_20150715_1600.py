# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0029_auto_20150715_1551'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stop',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='stop',
            name='longitude',
        ),
    ]
