# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0059_auto_20150510_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalapplication',
            name='first_aid',
            field=models.CharField(blank=True, choices=[(None, '--'), ('other', 'other')], max_length=10, default=''),
        ),
    ]
