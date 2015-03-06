# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0037_auto_20150306_1824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='croosupplement',
            name='assigned_croo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, related_name='croolings', null=True, to='croos.Croo'),
        ),
    ]
