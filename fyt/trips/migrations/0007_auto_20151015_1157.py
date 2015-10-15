# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0006_campsite_shelter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campsite',
            name='directions',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='campsite',
            name='shelter',
            field=models.CharField(verbose_name='shelter type', max_length=10, choices=[('TARP', 'tarp'), ('SHELTER', 'shelter'), ('CABIN', 'cabin')]),
        ),
        migrations.AlterField(
            model_name='campsite',
            name='water_source',
            field=models.TextField(verbose_name='closest water source', blank=True),
        ),
    ]
