# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0017_auto_20140912_2124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaderapplication',
            name='phone',
            field=models.CharField(max_length=255, verbose_name='Phone number'),
        ),
    ]
