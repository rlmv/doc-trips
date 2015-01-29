# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0009_auto_20150129_2144'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='triptemplate',
            options={'verbose_name': 'template', 'ordering': ['name']},
        ),
    ]
