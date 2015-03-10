# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('applications', '0040_auto_20150308_1614'),
    ]

    operations = [
        migrations.CreateModel(
            name='QualificationTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('trips_year', models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='crooapplicationgrade',
            name='qualification',
            field=models.ManyToManyField(to='applications.QualificationTag', blank=True),
            preserve_default=True,
        ),
    ]
