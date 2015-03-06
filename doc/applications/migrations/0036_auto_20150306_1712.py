# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0035_auto_20150303_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='crooapplicationgrade',
            name='scratchpad',
            field=models.TextField(verbose_name='scratchpad for question-specific notes', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplicationgrade',
            name='scratchpad',
            field=models.TextField(verbose_name='scratchpad for question-specific notes', default=''),
            preserve_default=False,
        ),
    ]
