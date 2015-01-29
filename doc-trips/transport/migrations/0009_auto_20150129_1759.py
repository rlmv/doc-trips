# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0008_auto_20150129_1753'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stop',
            old_name='location',
            new_name='address',
        ),
    ]
