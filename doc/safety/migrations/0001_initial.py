# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0034_auto_20150804_1229'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Incident',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('role', models.CharField(verbose_name='What is your role on Trips?', max_length=255)),
                ('where', models.TextField(verbose_name='Where during the trip did this occur?', help_text='trail name, campsite, Hanove, Lodge, etc')),
                ('when', models.DateTimeField(verbose_name='When did this incident occur?')),
                ('caller', models.CharField(verbose_name='Who called?', max_length=255)),
                ('caller_role', models.CharField(choices=[('TRIP_LEADER', 'Trip Leader'), ('CROO_MEMBER', 'Croo Member'), ('TRIPPEE', 'Trippee'), ('OTHER', 'Other')], max_length=20)),
                ('caller_number', models.CharField(max_length=20)),
                ('injuries', models.BooleanField(verbose_name='Did any injuries take place during this incident?', choices=[(True, 'Yes'), (False, 'No')], default=False)),
                ('subject', models.CharField(verbose_name='Who did this happen to?', blank=True, max_length=255)),
                ('subject_role', models.CharField(choices=[('TRIP_LEADER', 'Trip Leader'), ('CROO_MEMBER', 'Croo Member'), ('TRIPPEE', 'Trippee'), ('OTHER', 'Other')], blank=True, max_length=20)),
                ('desc', models.TextField(verbose_name='Describe the incident')),
                ('resp', models.TextField(verbose_name='What was the response to the incident')),
                ('outcome', models.TextField(verbose_name='What was the outcome of the response')),
                ('follow_up', models.TextField(verbose_name='Is any additional follow-up needed? If so, what?')),
                ('trip', models.ForeignKey(verbose_name='On what trip did this incident occur?', to='trips.Trip')),
                ('trips_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='db.TripsYear', editable=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
