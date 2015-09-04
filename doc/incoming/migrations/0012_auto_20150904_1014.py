# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0011_incomingstudent_cancelled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='cancelled',
            field=models.BooleanField(verbose_name='cancelled last-minute?', help_text='this Trippee will still be charged even though they are no longer going on a trip', default=False),
        ),
    ]
