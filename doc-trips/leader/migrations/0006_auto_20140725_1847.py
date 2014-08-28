# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0005_auto_20140725_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderapplication',
            name='preferred_sections',
            field=models.ManyToManyField(to='trip.Section', blank=True),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='preffered_sections',
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='available_sections',
            field=models.ManyToManyField(to='trip.Section', blank=True),
        ),
    ]
