# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-20 22:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0013_auto_20161102_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalapplication',
            name='document',
            field=models.FileField(blank=True, db_index=True, upload_to='', verbose_name='application answers'),
        ),
    ]
