# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0007_auto_20150129_1752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stop',
            name='distance',
            field=models.IntegerField(null=True),
        ),
    ]
