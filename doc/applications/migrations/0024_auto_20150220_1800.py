# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import doc.applications.models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db', '__first__'),
        ('applications', '0023_auto_20150220_1738'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrooApplicationGrade',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('grade', models.PositiveSmallIntegerField(validators=[doc.applications.models.validate_grade])),
                ('comment', models.TextField()),
                ('application', models.ForeignKey(editable=False, to='applications.CrooSupplement', related_name='grades')),
                ('grader', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False)),
                ('trips_year', models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LeaderApplicationGrade',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('grade', models.PositiveSmallIntegerField(validators=[doc.applications.models.validate_grade])),
                ('comment', models.TextField()),
                ('hard_skills', models.BooleanField(default=False)),
                ('soft_skills', models.BooleanField(default=False)),
                ('application', models.ForeignKey(editable=False, to='applications.LeaderSupplement', related_name='grades')),
                ('grader', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False)),
                ('trips_year', models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='croograde',
            name='application',
        ),
        migrations.RemoveField(
            model_name='croograde',
            name='grader',
        ),
        migrations.RemoveField(
            model_name='croograde',
            name='trips_year',
        ),
        migrations.DeleteModel(
            name='CrooGrade',
        ),
        migrations.RemoveField(
            model_name='leadergrade',
            name='application',
        ),
        migrations.RemoveField(
            model_name='leadergrade',
            name='grader',
        ),
        migrations.RemoveField(
            model_name='leadergrade',
            name='trips_year',
        ),
        migrations.DeleteModel(
            name='LeaderGrade',
        ),
    ]
