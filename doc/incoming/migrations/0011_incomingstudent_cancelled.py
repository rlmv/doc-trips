# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0010_auto_20150828_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='incomingstudent',
            name='cancelled',
            field=models.BooleanField(help_text='this Trippee will still be charged even though they are no longer going on a trip', default=False, verbose_name='cancelled last minute'),
            preserve_default=True,
        ),
    ]
