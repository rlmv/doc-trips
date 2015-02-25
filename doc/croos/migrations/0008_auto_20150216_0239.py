# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0007_auto_20150210_0218'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crooapplication',
            name='assigned_croo',
        ),
        migrations.RemoveField(
            model_name='crooapplication',
            name='potential_croos',
        ),
    ]
