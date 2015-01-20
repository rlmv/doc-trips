# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import sortedm2m.fields
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('trips_year', models.ForeignKey(editable=False, to='db.TripsYear')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrooApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('safety_dork_qualified', models.BooleanField(default=False)),
                ('safety_dork', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrooApplicationAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('answer', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrooApplicationGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('croo_application', models.ForeignKey(related_name='grades', to='croos.CrooApplication')),
                ('grader', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('trips_year', models.ForeignKey(editable=False, to='db.TripsYear')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrooApplicationQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('question', models.TextField()),
                ('ordering', models.IntegerField()),
                ('trips_year', models.ForeignKey(editable=False, to='db.TripsYear')),
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
            field=models.ForeignKey(editable=False, to='db.TripsYear'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crooapplication',
            name='answers',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='croos.CrooApplicationAnswer'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crooapplication',
            name='applicant',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crooapplication',
            name='assigned_croo',
            field=models.ForeignKey(null=True, blank=True, to='croos.Croo', related_name='croolings', on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crooapplication',
            name='potential_croos',
            field=models.ManyToManyField(related_name='potential_croolings', blank=True, to='croos.Croo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crooapplication',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear'),
            preserve_default=True,
        ),
    ]
