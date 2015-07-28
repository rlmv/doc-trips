# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0035_auto_20150723_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stop',
            name='cost',
            field=models.DecimalField(help_text='for external buses', decimal_places=2, max_digits=5, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='stop',
            name='route',
            field=models.ForeignKey(to='transport.Route', blank=True, null=True, related_name='stops', help_text='default bus route', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
