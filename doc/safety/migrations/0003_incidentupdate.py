# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db', '__first__'),
        ('safety', '0002_auto_20150806_1918'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncidentUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('caller', models.CharField(verbose_name='Who called?', max_length=255)),
                ('caller_role', models.CharField(choices=[('TRIP_LEADER', 'Trip Leader'), ('CROO_MEMBER', 'Croo Member'), ('TRIPPEE', 'Trippee'), ('OTHER', 'Other')], max_length=20)),
                ('caller_number', models.CharField(max_length=20)),
                ('update', models.TextField()),
                ('incident', models.ForeignKey(to='safety.Incident', editable=False)),
                ('trips_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, editable=False, to='db.TripsYear')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
