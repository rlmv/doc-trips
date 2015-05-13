# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0061_auto_20150512_2047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalapplication',
            name='fa_cert',
            field=models.CharField(verbose_name='first aid cert', default='', choices=[(None, '--'), ('FA', 'First Aid'), ('CPR', 'CPR'), ('FA/CPR', 'First Aid/CPR'), ('WFA', 'WFA'), ('WFR', 'WFR'), ('W-EMT', 'W-EMT'), ('EMT', 'EMT'), ('OEC', 'OEC'), ('other', 'other')], max_length=10, blank=True),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='fa_other',
            field=models.CharField(verbose_name='other first aid cert', default='', max_length=100, blank=True),
        ),
    ]
