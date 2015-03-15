# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0017_auto_20150315_1019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stop',
            name='route',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='transport.Route', related_name='stops', blank=True, null=True),
        ),
    ]
