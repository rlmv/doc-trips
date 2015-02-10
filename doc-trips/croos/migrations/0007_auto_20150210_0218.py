# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0006_auto_20150206_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crooapplicationanswer',
            name='answer',
            field=models.TextField(blank=True),
        ),
    ]
