# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0013_auto_20150129_1812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stop',
            name='directions',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='stop',
            name='route',
            field=models.ForeignKey(to='transport.Route', blank=True, null=True),
        ),
    ]
