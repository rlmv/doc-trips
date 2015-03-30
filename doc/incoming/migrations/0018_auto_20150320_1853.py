# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trippees', '0017_auto_20150320_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='green_fund_donation',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
    ]
