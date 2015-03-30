# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0025_auto_20150330_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='regular_exercise',
            field=models.CharField(choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Do you do enjoy cardiovascular exercise (running, biking, swimming, sports, etc.) on a regular basis?', max_length=3),
        ),
    ]
