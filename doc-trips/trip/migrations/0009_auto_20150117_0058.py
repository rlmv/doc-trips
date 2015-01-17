# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0008_auto_20140915_1559'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scheduledtrip',
            options={},
        ),
        migrations.AlterField(
            model_name='section',
            name='name',
            field=models.CharField(max_length=1, help_text='A, B, C, etc.'),
        ),
    ]
