# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0025_auto_20150624_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduledtrip',
            name='section',
            field=models.ForeignKey(to='trips.Section', on_delete=django.db.models.deletion.PROTECT, related_name='trips'),
        ),
    ]
