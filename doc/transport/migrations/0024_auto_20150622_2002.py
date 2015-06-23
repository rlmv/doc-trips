# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0023_auto_20150325_1427'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scheduledtransport',
            name='section',
        ),
        migrations.AlterField(
            model_name='scheduledtransport',
            name='date',
            field=models.DateField(),
        ),
    ]
