# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0020_generalapplication_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='croosupplement',
            name='assigned_croo',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='croos.Croo', related_name='croolings', null=True),
        ),
    ]
