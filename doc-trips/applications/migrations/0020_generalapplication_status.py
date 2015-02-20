# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0019_auto_20150219_1826'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalapplication',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('CROO', 'Croo'), ('LEADER', 'Leader'), ('LEADER_WAITLIST', 'Leader Waitlist'), ('REJECTED', 'Rejected'), ('CANCELED', 'Canceled')], default='PENDING', verbose_name='Application status', max_length=15),
            preserve_default=True,
        ),
    ]
