# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20150317_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dartmouthuser',
            name='name',
            field=models.CharField(db_index=True, max_length=255),
        ),
    ]
