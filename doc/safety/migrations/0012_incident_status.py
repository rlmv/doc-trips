# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('safety', '0011_auto_20150826_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='status',
            field=models.CharField(default='OPEN', choices=[('OPEN', 'open'), ('RESOLVED', 'resolved')], max_length=10),
            preserve_default=True,
        ),
    ]
