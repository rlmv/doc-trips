# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0018_auto_20150416_0926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptemplate',
            name='name',
            field=models.PositiveSmallIntegerField(db_index=True),
        ),
    ]
