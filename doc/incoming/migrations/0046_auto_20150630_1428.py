# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0045_auto_20150630_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='green_fund_donation',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
