# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion
import doc.applications.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db', '__first__'),
        ('applications', '0021_auto_20150220_1626'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrooGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('grade', models.DecimalField(decimal_places=1, max_digits=3, validators=[doc.applications.models.validate_grade])),
                ('comment', models.CharField(max_length=255)),
                ('grader', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('trips_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, editable=False, to='db.TripsYear')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LeaderGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('grade', models.DecimalField(decimal_places=1, max_digits=3, validators=[doc.applications.models.validate_grade])),
                ('comment', models.CharField(max_length=255)),
                ('hard_skills', models.BooleanField(default=False)),
                ('soft_skills', models.BooleanField(default=False)),
                ('grader', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('trips_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, editable=False, to='db.TripsYear')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
