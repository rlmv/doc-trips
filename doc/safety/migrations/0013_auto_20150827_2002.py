# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('safety', '0012_incident_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='incident',
            options={'ordering': ['status', '-when']},
        ),
    ]
