# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0005_auto_20150910_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='incomingstudent',
            name='cancelled_fee',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
