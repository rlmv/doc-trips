# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0006_auto_20150129_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='category',
            field=models.CharField(max_length=20, choices=[('INTERNAL', 'Internal'), ('EXTERNAL', 'External'), ('BOTH', 'Both')]),
        ),
        migrations.AlterField(
            model_name='stop',
            name='category',
            field=models.CharField(max_length=20, choices=[('INTERNAL', 'Internal'), ('EXTERNAL', 'External'), ('BOTH', 'Both')]),
        ),
        migrations.AlterField(
            model_name='stop',
            name='route',
            field=models.ForeignKey(null=True, to='transport.Route'),
        ),
    ]
