# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0002_auto_20150120_2315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crooapplication',
            name='answers',
            field=models.ManyToManyField(to='croos.CrooApplicationAnswer', blank=True, null=True),
        ),
    ]
