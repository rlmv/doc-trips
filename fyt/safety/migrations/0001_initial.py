# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Incident',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('caller', models.CharField(max_length=255, verbose_name='Who called?')),
                ('caller_role', models.CharField(max_length=20, choices=[('TRIP_LEADER', 'Trip Leader'), ('CROO_MEMBER', 'Croo Member'), ('TRIPPEE', 'Trippee'), ('OTHER', 'Other')])),
                ('caller_number', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=10, default='OPEN', choices=[('OPEN', 'open'), ('RESOLVED', 'resolved')])),
                ('where', models.TextField(help_text='trail name, campsite, Hanover, Lodge, etc', verbose_name='Where during the trip did this occur?')),
                ('when', models.DateTimeField(verbose_name='When did this incident occur?')),
                ('injuries', models.BooleanField(default=False, choices=[(True, 'Yes'), (False, 'No')], verbose_name='Did any injuries take place during this incident?')),
                ('subject', models.CharField(max_length=255, blank=True, verbose_name='Who did this happen to?')),
                ('subject_role', models.CharField(max_length=20, blank=True, choices=[('TRIP_LEADER', 'Trip Leader'), ('CROO_MEMBER', 'Croo Member'), ('TRIPPEE', 'Trippee'), ('OTHER', 'Other')])),
                ('desc', models.TextField(verbose_name='Describe the incident')),
                ('resp', models.TextField(verbose_name='What was the response to the incident?')),
                ('outcome', models.TextField(verbose_name='What was the outcome of the response?')),
                ('follow_up', models.TextField(verbose_name='Is any additional follow-up needed? If so, what?')),
            ],
            options={
                'ordering': ['status', '-when'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IncidentUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('caller', models.CharField(max_length=255, verbose_name='Who called?')),
                ('caller_role', models.CharField(max_length=20, choices=[('TRIP_LEADER', 'Trip Leader'), ('CROO_MEMBER', 'Croo Member'), ('TRIPPEE', 'Trippee'), ('OTHER', 'Other')])),
                ('caller_number', models.CharField(max_length=20)),
                ('update', models.TextField()),
                ('incident', models.ForeignKey(editable=False, to='safety.Incident', on_delete=models.CASCADE)),
                ('trips_year', models.ForeignKey(to='core.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False)),
            ],
            options={
                'ordering': ['created'],
            },
            bases=(models.Model,),
        ),
    ]
