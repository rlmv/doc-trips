# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='crooapplication',
            name='status',
            field=models.CharField(max_length=10, default='PENDING', verbose_name='Application status', choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('CANCELED', 'Cancelled')]),
            preserve_default=True,
        ),
    ]
