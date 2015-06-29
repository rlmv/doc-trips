# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0043_auto_20150629_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='financial_aid',
            field=models.PositiveSmallIntegerField(verbose_name='percentage financial assistance', default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
