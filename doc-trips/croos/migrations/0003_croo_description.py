# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0002_crooapplication_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='croo',
            name='description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
