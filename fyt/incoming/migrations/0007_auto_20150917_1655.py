# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0006_incomingstudent_cancelled_fee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='cancelled_fee',
            field=models.PositiveSmallIntegerField(help_text="if this is not set, and the student is marked as 'cancelled', the student will be charged the full cost of trips", null=True, blank=True, verbose_name='cancellation fee'),
        ),
    ]
