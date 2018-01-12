# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db', '0001_initial'),
        ('trips', '0001_initial'),
        ('safety', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidentupdate',
            name='user',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incident',
            name='trip',
            field=models.ForeignKey(blank=True, to='trips.Trip', help_text='leave blank if incident did not occur on a trip', null=True, verbose_name='On what trip did this incident occur?', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incident',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incident',
            name='user',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
