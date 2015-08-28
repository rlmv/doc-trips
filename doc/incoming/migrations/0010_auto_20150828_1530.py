# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0009_auto_20150824_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='med_info',
            field=models.TextField(blank=True, help_text='Use this field for additional medical info not provided in the registration, or simplified information if some details do not need to be provided to leaders and croos.'),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='notes',
            field=models.TextField(blank=True, help_text='These notes are displayed to the trippee along with their trip assignment.'),
        ),
    ]
