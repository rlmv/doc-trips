# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0044_auto_20150812_1940'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stop',
            options={'ordering': ['name']},
        ),
    ]
