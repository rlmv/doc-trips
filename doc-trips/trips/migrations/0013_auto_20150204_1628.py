# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0012_auto_20150129_2240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campsite',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='scheduledtrip',
            name='section',
            field=models.ForeignKey(to='trips.Section', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='scheduledtrip',
            name='template',
            field=models.ForeignKey(to='trips.TripTemplate', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='scheduledtrip',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='section',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='campsite1',
            field=models.ForeignKey(related_name='trip_night_1', to='trips.Campsite', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='campsite2',
            field=models.ForeignKey(related_name='trip_night_2', to='trips.Campsite', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='dropoff',
            field=models.ForeignKey(related_name='dropped_off_trips', to='transport.Stop', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='pickup',
            field=models.ForeignKey(related_name='picked_up_trips', to='transport.Stop', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='return_route',
            field=models.ForeignKey(null=True, related_name='returning_trips', to='transport.Route', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='triptype',
            field=models.ForeignKey(to='trips.TripType', verbose_name='trip type', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='triptype',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
