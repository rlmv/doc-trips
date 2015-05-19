# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0032_auto_20150519_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='is_international',
            field=models.CharField(verbose_name='Are you an International Student who plans on attending the International Student Orientation?', blank=True, choices=[('YES', 'yes'), ('NO', 'no')], max_length=3),
        ),
    ]
