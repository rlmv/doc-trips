# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('leader_application_available', models.DateTimeField()),
                ('leader_application_due', models.DateTimeField()),
                ('leader_assignment_posted', models.DateTimeField()),
                ('trippee_registration_available', models.DateTimeField()),
                ('trippee_assignment_posted', models.DateTimeField()),
                ('migration_date', models.DateTimeField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('cost', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TripsYear',
            fields=[
                ('year', models.PositiveIntegerField(unique=True, primary_key=True, serialize=False)),
                ('is_current', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='cost',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='calendar',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False),
            preserve_default=True,
        ),
    ]
