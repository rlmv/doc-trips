# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0014_auto_20151013_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='incomingstudent',
            name='hinman_box',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
