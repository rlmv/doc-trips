# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0005_auto_20150129_1736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stop',
            name='latitude',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='stop',
            name='longitude',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
