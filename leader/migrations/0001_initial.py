# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import leader.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaderApplication',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('trips_year', models.PositiveIntegerField()),
                ('status', models.CharField(default='PEND', choices=[('PEND', 'Pending'), ('ACC', 'Accepted'), ('WAIT', 'Waitlisted'), ('REJ', 'Rejected'), ('CROO', 'Croo'), ('CANC', 'Cancelled'), ('DEP', 'Deprecated'), ('DISQ', 'Disqualified')], max_length=4)),
                ('class_year', models.PositiveIntegerField()),
                ('tshirt_size', models.CharField(choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra large')], max_length=2)),
                ('gender', models.CharField(max_length=255)),
                ('hinman_box', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('offcampus_address', models.CharField(max_length=255, blank=True)),
                ('notes', models.CharField(max_length=255, blank=True)),
                ('assigned_trip', models.ForeignKey(null=True, to='trip.ScheduledTrip', blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LeaderGrade',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('grade', models.DecimalField(decimal_places=2, validators=[leader.models.validate_grade], max_digits=3)),
                ('comment', models.CharField(max_length=255)),
                ('hard_skills', models.BooleanField(default=False)),
                ('soft_skills', models.BooleanField(default=False)),
                ('grader', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('leader_application', models.ForeignKey(to='leader.LeaderApplication')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
