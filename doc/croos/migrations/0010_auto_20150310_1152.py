# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0009_auto_20150220_1800'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='croo',
            options={'ordering': ['name']},
        ),
    ]
