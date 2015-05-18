# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0028_auto_20150518_1159'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registration',
            name='summer_plans',
        ),
    ]
