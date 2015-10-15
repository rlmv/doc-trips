# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0003_auto_20150910_1637'),
    ]

    operations = [
        migrations.AddField(
            model_name='campsite',
            name='bear_bag',
            field=models.BooleanField(verbose_name='is a bear-bag required?', default=False),
        ),
        migrations.AddField(
            model_name='campsite',
            name='water_source',
            field=models.TextField(verbose_name='closest water source', default=''),
            preserve_default=False,
        ),
    ]
