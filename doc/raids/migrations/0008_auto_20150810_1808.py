# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raids', '0007_auto_20150810_1231'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='raid',
            options={'ordering': ['-created']},
        ),
    ]
