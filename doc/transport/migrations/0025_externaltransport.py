# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('trips', '0024_auto_20150505_1037'),
        ('transport', '0024_auto_20150622_2002'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalTransport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('route', models.ForeignKey(to='transport.Route', on_delete=django.db.models.deletion.PROTECT)),
                ('section', models.ForeignKey(to='trips.Section', on_delete=django.db.models.deletion.PROTECT)),
                ('trips_year', models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
