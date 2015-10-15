# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0004_auto_20151015_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campsite',
            name='bear_bag',
            field=models.BooleanField(default=False, verbose_name='bear-bag required?'),
        ),
    ]
