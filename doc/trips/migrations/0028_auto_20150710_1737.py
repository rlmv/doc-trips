# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0027_auto_20150710_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptype',
            name='gets_supplemental',
            field=models.BooleanField(verbose_name='gets a supplemental foodbox?', default=False),
        ),
        migrations.AlterField(
            model_name='triptype',
            name='half_kickin',
            field=models.PositiveSmallIntegerField(verbose_name='minimum # for a half foodbox', default=10),
        ),
    ]
