# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0060_auto_20150512_2038'),
    ]

    operations = [
        migrations.RenameField(
            model_name='generalapplication',
            old_name='first_aid_other',
            new_name='fa_other',
        ),
        migrations.RemoveField(
            model_name='generalapplication',
            name='first_aid',
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='fa_cert',
            field=models.CharField(max_length=10, default='', verbose_name='first aid cert', blank=True, choices=[(None, '--'), ('other', 'other')]),
            preserve_default=True,
        ),
    ]
