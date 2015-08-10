# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('safety', '0004_auto_20150806_2001'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidentupdate',
            name='role',
            field=models.CharField(default='', max_length=255, verbose_name='What is your role on Trips?'),
            preserve_default=False,
        ),
    ]
