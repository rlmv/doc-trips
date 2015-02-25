# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0005_auto_20150129_1630'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='triptype',
            options={'ordering': ['name']},
        ),
    ]
