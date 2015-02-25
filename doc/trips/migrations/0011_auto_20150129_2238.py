# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0010_auto_20150129_2226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptemplate',
            name='description_conclusion',
            field=models.TextField(verbose_name='Conclusion'),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='description_day1',
            field=models.TextField(verbose_name='Day 1'),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='description_day2',
            field=models.TextField(verbose_name='Day 2'),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='description_day3',
            field=models.TextField(verbose_name='Day 3'),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='description_introduction',
            field=models.TextField(verbose_name='Introduction'),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='description_summary',
            field=models.CharField(verbose_name='Summary', max_length=255),
        ),
    ]
