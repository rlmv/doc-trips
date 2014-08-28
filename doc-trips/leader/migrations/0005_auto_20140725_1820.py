# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0004_auto_20140725_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderapplication',
            name='available_sections',
            field=models.ManyToManyField(to='trip.Section'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='preffered_sections',
            field=models.ManyToManyField(to='trip.Section'),
            preserve_default=True,
        ),
    ]
