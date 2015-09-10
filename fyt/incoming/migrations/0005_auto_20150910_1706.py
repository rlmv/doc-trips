# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0004_auto_20150910_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='notes',
            field=models.TextField(blank=True, verbose_name='notes to trippee', help_text='These notes are displayed to the trippee along with their trip assignment.'),
        ),
    ]
