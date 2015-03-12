# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dartmouthuser',
            name='did',
            field=models.CharField(max_length=20, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dartmouthuser',
            name='netid',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
