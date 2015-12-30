# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0006_auto_20151013_2147'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalapplication',
            name='_hanover_in_fall',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], verbose_name='Are you planning to be in Hanover this fall?', default=False),
        ),
    ]
