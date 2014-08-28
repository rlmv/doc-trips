# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0004_auto_20140724_0425'),
    ]

    operations = [
        migrations.AddField(
            model_name='campsite',
            name='bugout',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='campsite',
            name='secret',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
