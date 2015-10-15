# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0008_auto_20151015_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='triptemplate',
            name='swimtest_required',
            field=models.BooleanField(default=False),
        ),
    ]
