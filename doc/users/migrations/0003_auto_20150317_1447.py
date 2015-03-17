# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150312_1052'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dartmouthuser',
            options={'ordering': ['name']},
        ),
    ]
