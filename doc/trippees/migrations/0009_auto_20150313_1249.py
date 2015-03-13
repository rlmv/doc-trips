# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trippees', '0008_auto_20150312_1142'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collegeinfo',
            old_name='ethnicity_code',
            new_name='ethnic_code',
        ),
        migrations.RemoveField(
            model_name='collegeinfo',
            name='did',
        ),
        migrations.RemoveField(
            model_name='collegeinfo',
            name='gender_code',
        ),
        migrations.AddField(
            model_name='collegeinfo',
            name='gender',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='collegeinfo',
            name='netid',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
    ]
