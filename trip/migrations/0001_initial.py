# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campsite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('trips_year', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=255)),
                ('capacity', models.PositiveSmallIntegerField()),
                ('directions', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScheduledTrip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('trips_year', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=1)),
                ('leaders_arrive', models.DateTimeField()),
                ('is_local', models.BooleanField(default=False)),
                ('is_exchange', models.BooleanField(default=False)),
                ('is_transfer', models.BooleanField(default=False)),
                ('is_international', models.BooleanField(default=False)),
                ('is_fysep', models.BooleanField(default=False)),
                ('is_native', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='scheduledtrip',
            name='section',
            field=models.ForeignKey(to='trip.Section'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='TripTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('trips_year', models.PositiveIntegerField()),
                ('name', models.PositiveSmallIntegerField()),
                ('description', models.CharField(max_length=255)),
                ('max_trippees', models.PositiveSmallIntegerField()),
                ('non_swimmers_allowed', models.BooleanField(default=True)),
                ('campsite_1', models.ForeignKey(to='trip.Campsite')),
                ('campsite_2', models.ForeignKey(to='trip.Campsite')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='scheduledtrip',
            name='template',
            field=models.ForeignKey(to='trip.TripTemplate'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='TripType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('trips_year', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=255)),
                ('leader_description', models.TextField()),
                ('trippee_description', models.TextField()),
                ('packing_list', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='triptemplate',
            name='trip_type',
            field=models.ForeignKey(to='trip.TripType'),
            preserve_default=True,
        ),
    ]
