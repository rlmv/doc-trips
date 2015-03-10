# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0015_auto_20150224_2104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptemplate',
            name='non_swimmers_allowed',
            field=models.BooleanField(verbose_name='non-swimmers allowed', default=True),
        ),
    ]
