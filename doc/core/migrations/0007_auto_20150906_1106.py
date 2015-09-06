# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150906_1012'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='settings',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='settings',
            name='trips_year',
        ),
        migrations.DeleteModel(
            name='Settings',
        ),
    ]
