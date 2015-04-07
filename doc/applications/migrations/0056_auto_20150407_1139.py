# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0055_auto_20150404_1205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalapplication',
            name='assigned_croo',
            field=models.ForeignKey(null=True, to='croos.Croo', blank=True, related_name='croo_members', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
