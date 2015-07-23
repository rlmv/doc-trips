# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0034_auto_20150723_1141'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stoporder',
            options={'ordering': ['distance']},
        ),
    ]
