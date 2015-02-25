# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0006_auto_20150129_2052'),
    ]

    operations = [
        migrations.RenameField(
            model_name='triptemplate',
            old_name='campsite_1',
            new_name='campsite1',
        ),
        migrations.RenameField(
            model_name='triptemplate',
            old_name='campsite_2',
            new_name='campsite2',
        ),
        migrations.RenameField(
            model_name='triptemplate',
            old_name='description',
            new_name='description_summary',
        ),
        migrations.AddField(
            model_name='triptemplate',
            name='description_conclusion',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='triptemplate',
            name='description_day1',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='triptemplate',
            name='description_day2',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='triptemplate',
            name='description_day3',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='triptemplate',
            name='description_introduction',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='triptemplate',
            name='revision_notes',
            field=models.TextField(default='', blank=True),
            preserve_default=False,
        ),
    ]
