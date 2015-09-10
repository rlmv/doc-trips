# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import doc.utils.lat_lng
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalBus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('category', models.CharField(max_length=20, choices=[('INTERNAL', 'Internal'), ('EXTERNAL', 'External')])),
            ],
            options={
                'ordering': ['category', 'vehicle', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScheduledTransport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('notes', models.TextField(help_text='for the bus driver')),
            ],
            options={
                'ordering': ['date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Stop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255, help_text='Plain text address, eg. Hanover, NH 03755. This must take you to the location in Google maps.', blank=True, default='')),
                ('lat_lng', models.CharField(max_length=255, default='', validators=[doc.utils.lat_lng.validate_lat_lng], help_text='Latitude & longitude coordinates, eg. 43.7030,-72.2895', verbose_name='coordinates', blank=True)),
                ('directions', models.TextField(blank=True)),
                ('cost_round_trip', models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='for external buses')),
                ('cost_one_way', models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='for external buses')),
                ('dropoff_time', models.TimeField(null=True, blank=True)),
                ('pickup_time', models.TimeField(null=True, blank=True)),
                ('distance', models.IntegerField(help_text='this rough distance from Hanover is used for bus routing')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StopOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField()),
                ('stop_type', models.CharField(max_length=10, choices=[('PICKUP', 'PICKUP'), ('DROPOFF', 'DROPOFF')])),
                ('bus', models.ForeignKey(to='transport.ScheduledTransport')),
            ],
            options={
                'ordering': ['order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('capacity', models.PositiveSmallIntegerField()),
                ('trips_year', models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
    ]
