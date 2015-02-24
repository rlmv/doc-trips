# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0013_auto_20150204_1628'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='section',
            options={'ordering': ['name']},
        ),
    ]
