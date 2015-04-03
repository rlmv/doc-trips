# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0053_auto_20150403_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portalcontent',
            name='day0_description',
            field=models.TextField(blank=True, help_text="description for leaders' first day, Gilman Island, etc.", verbose_name='day 0 description'),
        ),
        migrations.AlterField(
            model_name='portalcontent',
            name='day1_description',
            field=models.TextField(blank=True, help_text='post-Gilman, trippee arrival, swim test, safety talk, etc.', verbose_name='day 1 description'),
        ),
        migrations.AlterField(
            model_name='portalcontent',
            name='day5_description',
            field=models.TextField(blank=True, help_text='return to campust, pre-o', verbose_name='day 5 description'),
        ),
    ]
