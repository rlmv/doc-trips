# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('safety', '0010_auto_20150826_1746'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='incident',
            options={'ordering': ['-when']},
        ),
        migrations.AlterField(
            model_name='incident',
            name='trip',
            field=models.ForeignKey(to='trips.Trip', blank=True, null=True, verbose_name='On what trip did this incident occur?', help_text='leave blank if incident did not occur on a trip'),
        ),
    ]
