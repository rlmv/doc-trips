# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('raids', '0001_initial'),
        ('trips', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='raid',
            name='campsite',
            field=models.ForeignKey(to='trips.Campsite', null=True, blank=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='raid',
            name='trip',
            field=models.ForeignKey(to='trips.Trip', null=True, blank=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='raid',
            name='trips_year',
            field=models.ForeignKey(to='core.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
    ]
