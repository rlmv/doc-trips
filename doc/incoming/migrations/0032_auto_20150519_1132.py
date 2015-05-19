# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0031_auto_20150519_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='phone',
            field=models.CharField(verbose_name='phone number', max_length=20),
        ),
    ]
