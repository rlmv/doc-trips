# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-17 16:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0004_attendee_complete_sessions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendee',
            name='complete_sessions',
            field=models.ManyToManyField(blank=True, related_name='present', to='training.Session'),
        ),
    ]
