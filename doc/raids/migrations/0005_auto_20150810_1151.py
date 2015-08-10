# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('raids', '0004_auto_20150729_2246'),
    ]

    operations = [
        migrations.CreateModel(
            name='RaidInfo',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('info', models.TextField()),
                ('trips_year', models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='raidinfo',
            unique_together=set([('trips_year',)]),
        ),
    ]
