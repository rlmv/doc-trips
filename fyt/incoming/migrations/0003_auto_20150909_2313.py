# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db', '0001_initial'),
        ('transport', '0002_auto_20150909_2313'),
        ('trips', '0001_initial'),
        ('incoming', '0002_auto_20150909_2313'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='user',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='bus_assignment_from_hanover',
            field=models.ForeignKey(related_name='riders_from_hanover', on_delete=django.db.models.deletion.PROTECT, blank=True, to='transport.Stop', null=True, verbose_name='bus assignment FROM Hanover (one-way)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='bus_assignment_round_trip',
            field=models.ForeignKey(related_name='riders_round_trip', on_delete=django.db.models.deletion.PROTECT, blank=True, to='transport.Stop', null=True, verbose_name='bus assignment (round-trip)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='bus_assignment_to_hanover',
            field=models.ForeignKey(related_name='riders_to_hanover', on_delete=django.db.models.deletion.PROTECT, blank=True, to='transport.Stop', null=True, verbose_name='bus assignment TO Hanover (one-way)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='registration',
            field=models.OneToOneField(related_name='trippee', to='incoming.Registration', editable=False, null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='trip_assignment',
            field=models.ForeignKey(related_name='trippees', on_delete=django.db.models.deletion.PROTECT, to='trips.Trip', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='incomingstudent',
            unique_together=set([('netid', 'trips_year')]),
        ),
    ]
