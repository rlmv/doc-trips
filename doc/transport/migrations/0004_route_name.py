# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0003_stop_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='name',
            field=models.CharField(max_length=255, default='Grant Bus'),
            preserve_default=False,
        ),
    ]
