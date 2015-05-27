# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0034_auto_20150527_0024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='birthday',
            field=models.CharField(max_length=20),
        ),
    ]
