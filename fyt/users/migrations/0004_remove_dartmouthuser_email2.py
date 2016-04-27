# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_dartmouthuser_did'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dartmouthuser',
            name='email2',
        ),
    ]
