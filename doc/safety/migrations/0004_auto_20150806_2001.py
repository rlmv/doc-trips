# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('safety', '0003_incidentupdate'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='incidentupdate',
            options={'ordering': ['created']},
        ),
    ]
