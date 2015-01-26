# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campsite',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('capacity', models.PositiveSmallIntegerField()),
                ('directions', models.TextField()),
                ('bugout', models.TextField()),
                ('secret', models.TextField()),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScheduledTrip',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=1, help_text='A, B, C, etc.')),
                ('leaders_arrive', models.DateField()),
                ('is_local', models.BooleanField(default=False)),
                ('is_exchange', models.BooleanField(default=False)),
                ('is_transfer', models.BooleanField(default=False)),
                ('is_international', models.BooleanField(default=False)),
                ('is_fysep', models.BooleanField(default=False)),
                ('is_native', models.BooleanField(default=False)),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TripTemplate',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.PositiveSmallIntegerField()),
                ('description', models.CharField(max_length=255)),
                ('max_trippees', models.PositiveSmallIntegerField()),
                ('non_swimmers_allowed', models.BooleanField(default=True)),
                ('campsite_1', models.ForeignKey(related_name='trip_night_1', to='trips.Campsite')),
                ('campsite_2', models.ForeignKey(related_name='trip_night_2', to='trips.Campsite')),
            ],
            options={
                'verbose_name': 'template',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TripType',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('leader_description', models.TextField()),
                ('trippee_description', models.TextField()),
                ('packing_list', models.TextField(blank=True)),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='triptemplate',
            name='trip_type',
            field=models.ForeignKey(to='trips.TripType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='triptemplate',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='scheduledtrip',
            name='section',
            field=models.ForeignKey(to='trips.Section'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='scheduledtrip',
            name='template',
            field=models.ForeignKey(to='trips.TripTemplate'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='scheduledtrip',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='scheduledtrip',
            unique_together=set([('template', 'section', 'trips_year')]),
        ),
    ]
