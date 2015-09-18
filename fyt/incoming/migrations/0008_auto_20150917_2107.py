# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0007_auto_20150917_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='cancelled',
            field=models.BooleanField(help_text='This Trippee will still be charged even though they are no longer going on a trip', default=False, verbose_name='cancelled last-minute?'),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='cancelled_fee',
            field=models.PositiveSmallIntegerField(help_text="Customize the cancellation fee. Otherwise, by default a 'cancelled' student is charged the full cost of trips (adjusted by financial aid, if applicable). ", verbose_name='cancellation fee', blank=True, null=True),
        ),
    ]
