# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0019_auto_20150321_1238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='is_athlete',
            field=models.CharField(help_text="Each team has its own pre-season schedule. We are in close contact with fall coaches and will assign you to a trip section that works well for the team's pre-season schedule.", verbose_name='Are you a Fall varsity athlete (or Rugby or Water Polo)?', blank=True, choices=[('NO', 'No')], max_length=100),
        ),
        migrations.AlterField(
            model_name='registration',
            name='is_exchange',
            field=models.CharField(verbose_name='Are you an Exchange Student?', blank=True, choices=[('YES', 'yes'), ('NO', 'no')], max_length=3),
        ),
        migrations.AlterField(
            model_name='registration',
            name='is_fysep',
            field=models.CharField(verbose_name='Are you participating in the First Year Student Enrichment Program (FYSEP)?', blank=True, choices=[('YES', 'yes'), ('NO', 'no')], max_length=3),
        ),
        migrations.AlterField(
            model_name='registration',
            name='is_international',
            field=models.CharField(verbose_name='Are you an International Student?', blank=True, choices=[('YES', 'yes'), ('NO', 'no')], max_length=3),
        ),
        migrations.AlterField(
            model_name='registration',
            name='is_native',
            field=models.CharField(verbose_name='Are you a Native American Student and plan on attending the Native American student orientation?', blank=True, choices=[('YES', 'yes'), ('NO', 'no')], max_length=3),
        ),
        migrations.AlterField(
            model_name='registration',
            name='is_transfer',
            field=models.CharField(verbose_name='Are you a Transfer Student?', blank=True, choices=[('YES', 'yes'), ('NO', 'no')], max_length=3),
        ),
    ]
