# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0009_auto_20150313_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='collegeinfo',
            name='class_year',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
    ]
