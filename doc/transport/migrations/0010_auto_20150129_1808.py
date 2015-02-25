# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0009_auto_20150129_1759'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stop',
            options={'ordering': ['category']},
        ),
    ]
