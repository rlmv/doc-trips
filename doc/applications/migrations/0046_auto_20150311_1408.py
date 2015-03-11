# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0045_remove_crooapplicationgrade_potential_croos'),
    ]

    operations = [
        migrations.AddField(
            model_name='crooapplicationgrade',
            name='hard_skills',
            field=models.CharField(max_length=255, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='crooapplicationgrade',
            name='soft_skills',
            field=models.CharField(max_length=255, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='leaderapplicationgrade',
            name='hard_skills',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='leaderapplicationgrade',
            name='soft_skills',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
