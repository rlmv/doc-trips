# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0038_auto_20150730_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stoporder',
            name='order',
            field=models.PositiveSmallIntegerField(),
        ),
    ]
