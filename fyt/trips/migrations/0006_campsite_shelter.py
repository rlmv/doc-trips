# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0005_auto_20151015_1133'),
    ]

    operations = [
        migrations.AddField(
            model_name='campsite',
            name='shelter',
            field=models.CharField(default='TARP', verbose_name='sleeping arrangements', choices=[('TARP', 'tarp'), ('SHELTER', 'shelter'), ('CABIN', 'cabin')], max_length=10),
            preserve_default=False,
        ),
    ]
