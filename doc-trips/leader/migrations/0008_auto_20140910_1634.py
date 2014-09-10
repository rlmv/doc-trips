# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0007_auto_20140828_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaderapplication',
            name='available_sections',
            field=models.ManyToManyField(to='trip.Section', blank=True, related_name='available_leaders'),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='preferred_sections',
            field=models.ManyToManyField(to='trip.Section', blank=True, related_name='preferred_leaders'),
        ),
    ]
