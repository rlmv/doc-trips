# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0019_auto_20150420_1006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptype',
            name='name',
            field=models.CharField(db_index=True, max_length=255),
        ),
    ]
