# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0041_auto_20150811_1123'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scheduledtransport',
            options={'ordering': ['date']},
        ),
    ]
