# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-25 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0013_auto_20151028_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='triptype',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='hide this TripType from leader applications and incoming student registrations'),
        ),
    ]
