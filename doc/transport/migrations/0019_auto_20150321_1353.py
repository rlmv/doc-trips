# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0018_auto_20150315_1030'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stop',
            options={'ordering': ['route__category', 'route', 'name']},
        ),
        migrations.RemoveField(
            model_name='stop',
            name='category',
        ),
    ]
