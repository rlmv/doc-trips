# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0033_auto_20150519_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='incomingstudent',
            name='address',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='birthday',
            field=models.DateField(default=datetime.date(2015, 5, 27)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='phone',
            field=models.CharField(max_length=30, default=''),
            preserve_default=False,
        ),
    ]
