# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0022_auto_20150325_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduledtransport',
            name='date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='scheduledtransport',
            name='section',
            field=models.ForeignKey(null=True, blank=True, to='trips.Section'),
        ),
    ]
