# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0002_auto_20150128_2042'),
    ]

    operations = [
        migrations.AddField(
            model_name='stop',
            name='name',
            field=models.CharField(max_length=255, default='Errols farmstand'),
            preserve_default=False,
        ),
    ]
