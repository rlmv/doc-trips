# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0064_auto_20150512_2138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leadersupplement',
            name='community_building',
        ),
        migrations.RemoveField(
            model_name='leadersupplement',
            name='first_aid',
        ),
        migrations.RemoveField(
            model_name='leadersupplement',
            name='risk_management',
        ),
        migrations.RemoveField(
            model_name='leadersupplement',
            name='wilderness_skills',
        ),
    ]
