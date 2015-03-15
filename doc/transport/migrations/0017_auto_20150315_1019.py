# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0016_auto_20150204_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stop',
            name='route',
            field=models.ForeignKey(to='transport.Route', on_delete=django.db.models.deletion.PROTECT, null=True, blank=True),
        ),
    ]
