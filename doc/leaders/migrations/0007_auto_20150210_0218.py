# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leaders', '0006_auto_20150208_2225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaderapplicationanswer',
            name='answer',
            field=models.TextField(blank=True),
        ),
    ]
