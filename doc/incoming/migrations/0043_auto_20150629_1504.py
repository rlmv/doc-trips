# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0042_incomingstudent_financial_aid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='financial_aid',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], default=0),
        ),
    ]
