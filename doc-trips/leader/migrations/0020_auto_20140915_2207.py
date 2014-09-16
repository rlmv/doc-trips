# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0019_auto_20140915_2100'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sectionpreferences',
            name='info',
        ),
        migrations.AddField(
            model_name='sectionpreferences',
            name='choices',
            field=models.CharField(max_length=255, choices=[('hi', 'hi'), ('bye', 'bye')], default='hi'),
            preserve_default=False,
        ),
    ]
