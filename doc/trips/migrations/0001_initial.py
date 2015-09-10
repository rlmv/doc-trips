# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import doc.trips.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0001_initial'),
        ('transport', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campsite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('capacity', models.PositiveSmallIntegerField(null=True)),
                ('directions', models.TextField()),
                ('bugout', models.TextField()),
                ('secret', models.TextField()),
                ('trips_year', models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1, help_text='A, B, C, etc.', verbose_name='Section')),
                ('leaders_arrive', models.DateField()),
                ('is_local', models.BooleanField(default=False)),
                ('is_exchange', models.BooleanField(default=False)),
                ('is_transfer', models.BooleanField(default=False)),
                ('is_international', models.BooleanField(default=False)),
                ('is_fysep', models.BooleanField(default=False)),
                ('is_native', models.BooleanField(default=False)),
                ('trips_year', models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True, help_text='Trip-specific details such as weird timing. This information will be added to leader packets.')),
                ('dropoff_time', models.TimeField(null=True, blank=True)),
                ('pickup_time', models.TimeField(null=True, blank=True)),
                ('dropoff_route', models.ForeignKey(related_name='overridden_dropped_off_trips', on_delete=django.db.models.deletion.PROTECT, blank=True, to='transport.Route', null=True, help_text='leave blank to use default route from template')),
                ('pickup_route', models.ForeignKey(related_name='overridden_picked_up_trips', on_delete=django.db.models.deletion.PROTECT, blank=True, to='transport.Route', null=True, help_text='leave blank to use default route from template')),
                ('return_route', models.ForeignKey(related_name='overriden_returning_trips', on_delete=django.db.models.deletion.PROTECT, blank=True, to='transport.Route', null=True, help_text='leave blank to use default route from template')),
                ('section', models.ForeignKey(related_name='trips', on_delete=django.db.models.deletion.PROTECT, to='trips.Section')),
            ],
            options={
                'ordering': ('section__name', 'template__name'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TripTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.PositiveSmallIntegerField(validators=[doc.trips.models.validate_triptemplate_name], db_index=True)),
                ('description_summary', models.CharField(max_length=255, verbose_name='Summary')),
                ('max_trippees', models.PositiveSmallIntegerField()),
                ('non_swimmers_allowed', models.BooleanField(default=True, help_text="otherwise, trippees on the assignment page will be those who are at least 'BEGINNER' swimmers", verbose_name='non-swimmers allowed')),
                ('desc_intro', models.TextField(blank=True, verbose_name='Introduction')),
                ('desc_day1', models.TextField(blank=True, verbose_name='Day 1')),
                ('desc_day2', models.TextField(blank=True, verbose_name='Day 2')),
                ('desc_day3', models.TextField(blank=True, verbose_name='Day 3')),
                ('desc_conc', models.TextField(blank=True, verbose_name='Conclusion')),
                ('revisions', models.TextField(blank=True)),
                ('campsite1', models.ForeignKey(related_name='trip_night_1', on_delete=django.db.models.deletion.PROTECT, to='trips.Campsite', verbose_name='campsite 1')),
                ('campsite2', models.ForeignKey(related_name='trip_night_2', on_delete=django.db.models.deletion.PROTECT, to='trips.Campsite', verbose_name='campsite 2')),
                ('dropoff_stop', models.ForeignKey(related_name='dropped_off_trips', on_delete=django.db.models.deletion.PROTECT, to='transport.Stop')),
                ('pickup_stop', models.ForeignKey(related_name='picked_up_trips', on_delete=django.db.models.deletion.PROTECT, to='transport.Stop')),
                ('return_route', models.ForeignKey(related_name='returning_trips', on_delete=django.db.models.deletion.PROTECT, to='transport.Route', null=True)),
                ('trips_year', models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TripType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('leader_description', models.TextField()),
                ('trippee_description', models.TextField()),
                ('packing_list', models.TextField(blank=True)),
                ('half_kickin', models.PositiveSmallIntegerField(default=10, verbose_name='minimum # for a half foodbox')),
                ('gets_supplemental', models.BooleanField(default=False, verbose_name='gets a supplemental foodbox?')),
                ('trips_year', models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='triptemplate',
            name='triptype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='trips.TripType', verbose_name='trip type'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='trip',
            name='template',
            field=models.ForeignKey(to='trips.TripTemplate', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='trip',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='trip',
            unique_together=set([('template', 'section', 'trips_year')]),
        ),
    ]
