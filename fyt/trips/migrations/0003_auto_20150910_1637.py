# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0002_auto_20150910_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campsite',
            name='secret',
            field=models.TextField(help_text='door codes and other secret info'),
        ),
    ]
