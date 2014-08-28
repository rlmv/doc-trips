# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadergrade',
            name='trips_year',
            field=models.PositiveIntegerField(editable=False, default=2014),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='trips_year',
            field=models.PositiveIntegerField(editable=False),
        ),
    ]
