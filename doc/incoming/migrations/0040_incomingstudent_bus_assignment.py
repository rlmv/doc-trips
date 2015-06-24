# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0025_externaltransport'),
        ('incoming', '0039_delete_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='incomingstudent',
            name='bus_assignment',
            field=models.ForeignKey(null=True, to='transport.ExternalTransport', on_delete=django.db.models.deletion.PROTECT, blank=True),
            preserve_default=True,
        ),
    ]
