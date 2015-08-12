# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0042_auto_20150812_1125'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stop',
            old_name='cost',
            new_name='cost_round_trip',
        ),
        migrations.AddField(
            model_name='stop',
            name='cost_one_way',
            field=models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='for external buses'),
            preserve_default=True,
        ),
    ]
