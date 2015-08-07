# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('safety', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 6, 19, 18, 55, 676780), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='incident',
            name='where',
            field=models.TextField(verbose_name='Where during the trip did this occur?', help_text='trail name, campsite, Hanover, Lodge, etc'),
        ),
    ]
