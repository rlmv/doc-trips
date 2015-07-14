# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0026_auto_20150710_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptype',
            name='gets_supplemental',
            field=models.BooleanField(default=False, verbose_name='gets a SUPPLEMENTAL foodbox?'),
        ),
        migrations.AlterField(
            model_name='triptype',
            name='half_kickin',
            field=models.PositiveSmallIntegerField(default=10, verbose_name='minimum # for a HALF foodbox'),
        ),
    ]
