# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0036_auto_20150306_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crooapplicationgrade',
            name='scratchpad',
            field=models.TextField(blank=True, verbose_name='scratchpad for question-specific notes'),
        ),
        migrations.AlterField(
            model_name='leaderapplicationgrade',
            name='scratchpad',
            field=models.TextField(blank=True, verbose_name='scratchpad for question-specific notes'),
        ),
    ]
