# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0019_auto_20150321_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='category',
            field=models.CharField(max_length=20, choices=[('INTERNAL', 'Internal'), ('EXTERNAL', 'External')]),
        ),
    ]
