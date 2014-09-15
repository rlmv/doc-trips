# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0007_auto_20140830_2328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptype',
            name='packing_list',
            field=models.TextField(blank=True),
        ),
    ]
