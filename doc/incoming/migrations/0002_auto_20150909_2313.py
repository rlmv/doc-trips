# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0001_initial'),
        ('incoming', '0001_initial'),
        ('transport', '0002_auto_20150909_2313'),
        ('trips', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='available_sections',
            field=models.ManyToManyField(to='trips.Section', related_name='available_trippees', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='available_triptypes',
            field=models.ManyToManyField(to='trips.TripType', related_name='available_trippees', blank=True, verbose_name='available types of trips'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='bus_stop_from_hanover',
            field=models.ForeignKey(related_name='requests_from_hanover', on_delete=django.db.models.deletion.PROTECT, to='transport.Stop', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='bus_stop_round_trip',
            field=models.ForeignKey(related_name='requests_round_trip', on_delete=django.db.models.deletion.PROTECT, blank=True, to='transport.Stop', null=True, verbose_name='Where would you like to be bussed from/to?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='bus_stop_to_hanover',
            field=models.ForeignKey(related_name='requests_to_hanover', on_delete=django.db.models.deletion.PROTECT, to='transport.Stop', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='firstchoice_triptype',
            field=models.ForeignKey(related_name='firstchoice_triptype', blank=True, to='trips.TripType', null=True, verbose_name='first choice trip types'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='preferred_sections',
            field=models.ManyToManyField(to='trips.Section', related_name='prefering_trippees', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='preferred_triptypes',
            field=models.ManyToManyField(to='trips.TripType', related_name='preferring_trippees', blank=True, verbose_name='preferred types of trips'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='unavailable_sections',
            field=models.ManyToManyField(to='trips.Section', related_name='unavailable_trippees', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='registration',
            name='unavailable_triptypes',
            field=models.ManyToManyField(to='trips.TripType', related_name='unavailable_trippees', blank=True, verbose_name='unavailable trip types'),
            preserve_default=True,
        ),
    ]
