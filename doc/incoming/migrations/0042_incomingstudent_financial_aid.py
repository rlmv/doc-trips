# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0041_auto_20150624_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='incomingstudent',
            name='financial_aid',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
