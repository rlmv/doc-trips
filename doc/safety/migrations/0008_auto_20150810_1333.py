# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('safety', '0007_auto_20150810_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incident',
            name='outcome',
            field=models.TextField(verbose_name='What was the outcome of the response?'),
        ),
        migrations.AlterField(
            model_name='incident',
            name='resp',
            field=models.TextField(verbose_name='What was the response to the incident?'),
        ),
    ]
