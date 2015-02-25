# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0011_auto_20150129_2238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptemplate',
            name='description_conclusion',
            field=models.TextField(verbose_name='Conclusion', blank=True),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='description_day1',
            field=models.TextField(verbose_name='Day 1', blank=True),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='description_day2',
            field=models.TextField(verbose_name='Day 2', blank=True),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='description_day3',
            field=models.TextField(verbose_name='Day 3', blank=True),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='description_introduction',
            field=models.TextField(verbose_name='Introduction', blank=True),
        ),
    ]
