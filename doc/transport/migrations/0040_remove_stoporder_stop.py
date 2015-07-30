# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0039_auto_20150730_0925'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stoporder',
            name='stop',
        ),
    ]
