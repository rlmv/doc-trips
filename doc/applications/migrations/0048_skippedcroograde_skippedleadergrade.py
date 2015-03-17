# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('applications', '0047_auto_20150317_1523'),
    ]

    operations = [
        migrations.CreateModel(
            name='SkippedCrooGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('application', models.ForeignKey(to='applications.CrooSupplement', editable=False)),
                ('trips_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, editable=False, to='db.TripsYear')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SkippedLeaderGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('application', models.ForeignKey(to='applications.LeaderSupplement', editable=False)),
                ('trips_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, editable=False, to='db.TripsYear')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
