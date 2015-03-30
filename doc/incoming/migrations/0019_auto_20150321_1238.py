# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0018_auto_20150320_1853'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='is_athlete',
            field=models.CharField(default='', blank=True, max_length=100, help_text="Each team has its own pre-season schedule. We are in close contact with fall coaches and will assign you to a trip section that works well for the team's pre-season schedule."),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='is_exchange',
            field=models.BooleanField(default=False, verbose_name='Exchange Student?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='is_fysep',
            field=models.BooleanField(default=False, verbose_name='Participating in the First Year Student Enrichment Program (FYSEP)?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='is_international',
            field=models.BooleanField(default=False, verbose_name='International Student?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='is_native',
            field=models.BooleanField(default=False, verbose_name='Native American Student?', help_text='Choose yes if you plan on attending the Native American student orientation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='is_transfer',
            field=models.BooleanField(default=False, verbose_name='Transfer Student?'),
            preserve_default=True,
        ),
    ]
