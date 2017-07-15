# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-14 16:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0005_auto_20170714_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transportconfig',
            name='hanover',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='transport.Stop'),
        ),
        migrations.AlterField(
            model_name='transportconfig',
            name='lodge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='transport.Stop'),
        ),
    ]