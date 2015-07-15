# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0031_auto_20150715_1636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stop',
            name='address',
            field=models.CharField(default='', max_length=255, help_text='Plain text address, eg. Hanover, NH 03755. This must take you to the location in Google maps.', blank=True),
        ),
        migrations.AlterField(
            model_name='stop',
            name='distance',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
