# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Croo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrooApplication',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('safety_dork_qualified', models.BooleanField(default=False)),
                ('safety_dork', models.BooleanField(default=False)),
                ('applicant', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('assigned_croo', models.ForeignKey(related_name='croolings', to='croos.Croo', blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('potential_croos', models.ManyToManyField(related_name='potential_croolings', to='croos.Croo', blank=True)),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrooApplicationAnswer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('answer', models.TextField()),
                ('application', models.ForeignKey(related_name='answers', to='croos.CrooApplication', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrooApplicationGrade',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('grade', models.IntegerField()),
                ('comments', models.TextField()),
                ('application', models.ForeignKey(related_name='grades', to='croos.CrooApplication')),
                ('grader', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrooApplicationQuestion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('question', models.TextField()),
                ('ordering', models.IntegerField()),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='crooapplicationanswer',
            name='question',
            field=models.ForeignKey(to='croos.CrooApplicationQuestion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crooapplicationanswer',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False),
            preserve_default=True,
        ),
    ]
