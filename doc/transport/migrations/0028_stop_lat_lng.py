# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0027_auto_20150628_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='stop',
            name='lat_lng',
            field=models.CharField(default='', blank=True, max_length=255),
            preserve_default=True,
        ),
    ]
