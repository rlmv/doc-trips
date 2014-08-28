# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0002_auto_20140723_1855'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledtrip',
            name='trips_year',
            field=models.PositiveIntegerField(editable=False, default=2014),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='campsite',
            name='trips_year',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='section',
            name='trips_year',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='trips_year',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='triptype',
            name='trips_year',
            field=models.PositiveIntegerField(editable=False),
        ),
    ]
