# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0004_auto_20150128_2045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campsite',
            name='capacity',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]
