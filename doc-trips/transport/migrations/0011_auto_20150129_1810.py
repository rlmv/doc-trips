# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0010_auto_20150129_1808'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='route',
            options={'ordering': ['category']},
        ),
        migrations.AlterModelOptions(
            name='vehicle',
            options={'ordering': ['name']},
        ),
    ]
