# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0014_auto_20150224_2102'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='campsite',
            options={'ordering': ['name']},
        ),
    ]
