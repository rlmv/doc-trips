# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0029_remove_registration_summer_plans'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='sailing_experience',
            field=models.TextField(default='', verbose_name='Please describe your sailing experience.', blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='registration',
            name='camping_experience',
            field=models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Have you ever spent a night camping under a tarp?'),
        ),
    ]
