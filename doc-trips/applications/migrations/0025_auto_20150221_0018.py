# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0024_auto_20150220_1800'),
    ]

    operations = [
        migrations.RenameField(
            model_name='leadersupplement',
            old_name='supplement',
            new_name='document',
        ),
    ]
