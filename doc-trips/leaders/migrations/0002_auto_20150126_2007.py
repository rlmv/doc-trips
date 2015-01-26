# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('trips', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leaders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderapplication',
            name='assigned_trip',
            field=models.ForeignKey(related_name='leaders', to='trips.ScheduledTrip', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='available_sections',
            field=models.ManyToManyField(related_name='available_leaders', to='trips.Section', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='available_triptypes',
            field=models.ManyToManyField(verbose_name='Available types of trips', to='trips.TripType', blank=True, related_name='available_triptypes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='preferred_sections',
            field=models.ManyToManyField(related_name='preferred_leaders', to='trips.Section', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='preferred_triptypes',
            field=models.ManyToManyField(verbose_name='Preferred types of trips', to='trips.TripType', blank=True, related_name='preferred_leaders'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='user',
            field=models.ForeignKey(verbose_name='Applicant', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
