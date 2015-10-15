# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0013_auto_20151013_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='epipen',
            field=models.NullBooleanField(choices=[(True, 'Yes'), (False, 'No')], verbose_name='Do you carry an EpiPen? If yes, please bring it with you on Trips.', default=None),
        ),
    ]
