# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0040_incomingstudent_bus_assignment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='bus_assignment',
            field=models.ForeignKey(null=True, blank=True, to='transport.Stop', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
