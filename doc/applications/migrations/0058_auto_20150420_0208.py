# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0057_generalapplication_safety_lead'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leadersupplement',
            name='document',
            field=models.FileField(db_index=True, upload_to='', blank=True, verbose_name='leader application answers'),
        ),
    ]
