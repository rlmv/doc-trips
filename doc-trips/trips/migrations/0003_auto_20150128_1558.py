# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0002_auto_20150128_0346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptemplate',
            name='triptype',
            field=models.ForeignKey(to='trips.TripType', verbose_name='trip type'),
        ),
    ]
