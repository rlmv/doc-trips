# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScheduledTransport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('route', models.ForeignKey(to='transport.Route')),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Stop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('location', models.CharField(max_length=255, help_text='Plain text address, eg. Hanover, NH 03755. This must take you to the location in Google maps.')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('primary_route', models.ForeignKey(to='transport.Route')),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('capacity', models.PositiveSmallIntegerField()),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='route',
            name='vehicle',
            field=models.ForeignKey(to='transport.Vehicle'),
            preserve_default=True,
        ),
    ]
