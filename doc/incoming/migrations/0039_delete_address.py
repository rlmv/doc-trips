# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0038_auto_20150531_1413'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Address',
        ),
    ]
