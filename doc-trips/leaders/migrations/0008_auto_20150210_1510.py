# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leaders', '0007_auto_20150210_0218'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderapplication',
            name='medical_certifications',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='relevant_experience',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
