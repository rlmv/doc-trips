# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trips', '0030_rename_ScheduledTrip_to_Trip'),
        ('db', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('comment', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('trips_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='db.TripsYear', editable=False)),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Raid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('date', models.DateField()),
                ('plan', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('campsite', models.ForeignKey(blank=True, to='trips.Campsite', null=True)),
                ('trip', models.ForeignKey(blank=True, to='trips.Trip', null=True)),
                ('trips_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='db.TripsYear', editable=False)),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
