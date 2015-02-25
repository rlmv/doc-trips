# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0014_auto_20150218_2253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='croosupplement',
            name='document',
            field=models.FileField(upload_to='', blank=True, verbose_name='Croo Application Answers'),
        ),
        migrations.AlterField(
            model_name='leadersupplement',
            name='supplement',
            field=models.FileField(upload_to='', blank=True, verbose_name='leader application answers'),
        ),
    ]
